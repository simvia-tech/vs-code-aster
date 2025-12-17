import * as vscode from 'vscode';
import * as path from 'path';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
} from 'vscode-languageclient/node';
import { StatusBar } from './StatusBar';
/**
 * Singleton class to manage the Python LSP client for Code-Aster.
 * Handles client creation, start, restart, notifications, and editor listeners.
 */
export class LspServer {

    private static _instance: LspServer;
    private _client?: LanguageClient;

    private constructor() { }

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
        if (!this._client) {
            this._client = await this.createClient(context);
        }

        this._client.start()
            .then(() => {
                vscode.window.showInformationMessage('LSP Python Code-Aster ready!');
                this.attachEditorListeners();
            })
            .catch((err: any) => {
                vscode.window.showErrorMessage('Error starting LSP Python: ' + err.message);
            });

        this._client.onDidChangeState(e => console.log('LSP client state changed:', e));
        
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
        const serverOptions: ServerOptions = {
            command: pythonExecutablePath,
            args: [serverModule],
            transport: TransportKind.stdio,
            options: {
                env: {
                    ...process.env,
                    PYTHONPATH: context.asAbsolutePath('python'),
                },
            },
        };

        const clientOptions: LanguageClientOptions = {
            documentSelector: [{ scheme: 'file', language: 'comm' }],
            synchronize: {
                fileEvents: vscode.workspace.createFileSystemWatcher('**/*.comm'),
            },
        };

        return new LanguageClient(
            'pythonLanguageServer',
            'Python Language Server',
            serverOptions,
            clientOptions
        );
    }

    /**
     * Adds editor listeners for parameter hints
     */
    private async attachEditorListeners() {
        vscode.workspace.onDidChangeTextDocument(event => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || event.document !== editor.document) { return; }

            const changes = event.contentChanges;
            if (changes.length === 0) { return; }

            //activate signature and completion triggers
            const lastChange = changes[changes.length - 1];
            if (['(',','].includes(lastChange.text) && editor.document.languageId === 'comm') {
                vscode.commands.executeCommand('editor.action.triggerParameterHints');
            }
        });
    }

    /**
     * Restarts the LSP server
     */
    public async restart() {
        if (this._client && this._client.isRunning()) {
            await this._client.stop();
        }

        this._client?.start()
            .then(() => vscode.window.showInformationMessage('LSP Python Code-Aster restarted!'))
            .catch((err: any) => vscode.window.showErrorMessage('Error restarting LSP Python: ' + err.message));
    }

    /**
     * Deactivates the LSP server
     */
    public deactivate(): Thenable<void> | undefined {
        if (!this._client) { return undefined; }
        return this._client.stop();
    }
}
