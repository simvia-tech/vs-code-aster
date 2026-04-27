import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from 'vscode-languageclient/node';
import { StatusBar } from './StatusBar';
import { SUPPORTED_COMM_EXTENSIONS } from './VisuManager';
import { spawn } from 'child_process';
import {
  caveFilePath,
  resolveCatalogPath,
  getCatalogChannel,
  reconcileCatalogCache,
} from './CatalogResolver';
/**
 * Singleton class to manage the Python LSP client for Code-Aster.
 * Handles client creation, start, restart, notifications, and editor listeners.
 */
export class LspServer {
  private static _instance: LspServer;
  private _client?: LanguageClient;
  private _context?: vscode.ExtensionContext;
  private _caveWatcher?: fs.FSWatcher;
  private _caveDebounce?: NodeJS.Timeout;
  // Kept as a class field so `restart()` can mutate `options.env` before
  // bouncing the server — `LanguageClient` re-reads it on the next spawn.
  private _serverOptions?: { command: string; args: string[]; options: { env: NodeJS.ProcessEnv } };

  private constructor() {}

  public static get instance(): LspServer {
    if (!LspServer._instance) {
      LspServer._instance = new LspServer();
    }
    return LspServer._instance;
  }

  public get client(): LanguageClient {
    if (!this._client) {
      throw new Error('LSP client has not been initialized yet.');
    }
    return this._client;
  }

  /**
   * Starts the LSP client
   */
  public async start(context: vscode.ExtensionContext) {
    this._context = context;
    // Reconcile on-disk caches against what docker currently has. If an
    // image was removed externally (docker rmi, cave internal cleanup), the
    // matching extracted catalog lingers and our resolver would still serve
    // it. Clear orphans before resolveCatalogPath runs.
    await reconcileOnStartup();
    if (!this._client) {
      this._client = await this.createClient(context);
    }

    this.watchCaveFile();

    void vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Window,
        title: 'Starting code_aster language server…',
      },
      () =>
        this._client!.start()
          .then(() => {
            this.attachEditorListeners();
          })
          .catch((err: any) => {
            vscode.window.showErrorMessage(
              'Error starting code_aster language server: ' + err.message
            );
          })
    );

    this._client.onDidChangeState((e) => console.log('LSP client state changed:', e));

    this._client.onNotification('logParser', (params: { text: string }) => {
      console.log(`${params.text}`);
    });

    //TO DO : reload the bar
    this._client.onNotification('reloadStatusBar', (params) => {
      StatusBar.instance.onEditorChange(vscode.window.activeTextEditor);
    });
  }

  /**
   * Creates the LanguageClient for Python LSP
   */
  private async createClient(context: vscode.ExtensionContext): Promise<LanguageClient> {
    const serverModule = context.asAbsolutePath(path.join('python', 'lsp', 'server.py'));

    const config = vscode.workspace.getConfiguration('vs-code-aster');
    const pythonExecutablePath = config.get<string>('pythonExecutablePath', 'python3');
    const commFileExtensions = config.get<string[]>(
      'commFileExtensions',
      SUPPORTED_COMM_EXTENSIONS
    );

    // Build file system watcher patterns
    const watchPatterns = commFileExtensions.map((ext) => `**/*${ext}`);

    const resolved = await resolveCatalogPath();
    const env: NodeJS.ProcessEnv = {
      ...process.env,
      PYTHONPATH: context.asAbsolutePath('python'),
    };
    if (resolved.path) {
      env.VS_CODE_ASTER_CATA_PATH = resolved.path;
    }
    getCatalogChannel().appendLine(
      `[catalog] LSP will start with source=${resolved.source}, path=${resolved.path ?? '(vendored)'}`
    );

    const serverOptions: ServerOptions = {
      command: pythonExecutablePath,
      args: [serverModule],
      transport: TransportKind.stdio,
      options: { env },
    };
    // Save so restart() can refresh env without rebuilding the client.
    this._serverOptions = {
      command: pythonExecutablePath,
      args: [serverModule],
      options: { env },
    };

    const clientOptions: LanguageClientOptions = {
      documentSelector: [{ scheme: 'file', language: 'comm' }],
      synchronize: {
        fileEvents: vscode.workspace.createFileSystemWatcher(`{${watchPatterns.join(',')}}`),
      },
    };

    return new LanguageClient(
      // Internal id stays for backward-compat with any user-saved trace
      // settings; only the display name (next arg) is user-visible.
      'pythonLanguageServer',
      'code_aster: Language Server',
      serverOptions,
      clientOptions
    );
  }

  /**
   * Adds editor listeners for parameter hints
   */
  private async attachEditorListeners() {
    vscode.workspace.onDidChangeTextDocument((event) => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || event.document !== editor.document) {
        return;
      }

      const changes = event.contentChanges;
      if (changes.length === 0) {
        return;
      }

      if (editor.document.languageId !== 'comm') {
        return;
      }

      // Auto-closing pairs collapse a `(` keystroke into a single change
      // whose text is `()`, so element-equality on the change list misses
      // it. Use substring matching across all changes.
      const typed = changes.map((c) => c.text).join('');

      // Hide-then-trigger: VS Code's suggest widget can lock into a
      // sticky "No suggestions" state when an LSP returns an empty list,
      // and `triggerSuggest` alone won't re-open it. Explicitly hiding
      // first guarantees a fresh query.
      const popSuggest = () => {
        vscode.commands.executeCommand('hideSuggestWidget');
        setTimeout(() => vscode.commands.executeCommand('editor.action.triggerSuggest'), 0);
      };

      if (typed.includes('(')) {
        vscode.commands.executeCommand('editor.action.triggerParameterHints');
        popSuggest();
        return;
      }
      if (typed.includes(',')) {
        popSuggest();
        return;
      }
      if (typed.includes('=')) {
        popSuggest();
        return;
      }
      if (typed.includes('\n')) {
        popSuggest();
        return;
      }
      if (typed === ' ') {
        const pos = editor.selection.active;
        const before = editor.document
          .lineAt(pos.line)
          .text.slice(0, pos.character)
          .replace(/\s+$/, '');
        if (before.endsWith(',')) {
          popSuggest();
        }
      }
    });
  }

  /**
   * Restarts the LSP server
   */
  public async restart() {
    // Reuse the same LanguageClient instance — constructing a new one
    // would (a) re-register hover/completion/code-action providers
    // (duplicate tooltips), (b) leave the old client's registrations in
    // VS Code's provider list (the "Client got disposed and can't be
    // restarted" error). stop() + start() on the same client avoids
    // both. We still need fresh env vars on `cave use`; LanguageClient
    // re-reads `serverOptions.options.env` on each spawn, so mutating
    // it in place is enough.
    if (!this._client || !this._context) {
      // First-time start path — defer to start().
      if (this._context) {
        await this.start(this._context);
      }
      return;
    }

    try {
      const resolved = await resolveCatalogPath();
      if (this._serverOptions) {
        const env = this._serverOptions.options.env;
        delete env.VS_CODE_ASTER_CATA_PATH;
        if (resolved.path) {
          env.VS_CODE_ASTER_CATA_PATH = resolved.path;
        }
      }
      getCatalogChannel().appendLine(
        `[catalog] LSP will restart with source=${resolved.source}, path=${resolved.path ?? '(vendored)'}`
      );
    } catch (err: any) {
      getCatalogChannel().appendLine(
        `[catalog] failed to resolve before restart: ${err?.message ?? err}`
      );
    }

    const client = this._client;
    void vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Window,
        title: 'Restarting code_aster language server…',
      },
      async () => {
        try {
          if (client.isRunning()) {
            await client.stop();
          }
        } catch (err: any) {
          getCatalogChannel().appendLine(`[lsp] stop() during restart: ${err?.message ?? err}`);
        }
        try {
          await client.start();
        } catch (err: any) {
          vscode.window.showErrorMessage(
            'Error restarting code_aster language server: ' + (err?.message ?? err)
          );
        }
      }
    );
  }

  private watchCaveFile() {
    if (this._caveWatcher) {
      return;
    }
    const cavePath = caveFilePath();
    const channel = getCatalogChannel();
    try {
      this._caveWatcher = fs.watch(cavePath, () => {
        if (this._caveDebounce) {
          clearTimeout(this._caveDebounce);
        }
        this._caveDebounce = setTimeout(() => {
          channel.appendLine(`[catalog] ~/.cave changed, restarting LSP`);
          void this.restart();
        }, 500);
      });
      channel.appendLine(`[catalog] watching ${cavePath}`);
    } catch (err: any) {
      channel.appendLine(`[catalog] cannot watch ${cavePath}: ${err?.message ?? err}`);
    }
  }

  /**
   * Deactivates the LSP server
   */
  public deactivate(): Thenable<void> | undefined {
    if (!this._client) {
      return undefined;
    }
    return this._client.stop();
  }
}

async function reconcileOnStartup(): Promise<void> {
  const installed = await new Promise<string[]>((resolve) => {
    const child = spawn('docker', ['images', '--format', '{{.Tag}}', 'simvia/code_aster'], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let out = '';
    const timer = setTimeout(() => child.kill('SIGKILL'), 5_000);
    child.stdout.on('data', (d) => (out += d.toString()));
    child.on('error', () => {
      clearTimeout(timer);
      resolve([]);
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      if (code !== 0) {
        return resolve([]);
      }
      resolve(
        Array.from(
          new Set(
            out
              .split(/\r?\n/)
              .map((s) => s.trim())
              .filter((s) => s && s !== '<none>')
          )
        )
      );
    });
  });
  if (installed.length === 0) {
    // Don't reconcile against an empty list — if docker is simply unavailable
    // we'd nuke all caches and force re-extraction next time docker comes
    // back. Treat "no info" as "keep what we have".
    return;
  }
  reconcileCatalogCache(installed);
}
