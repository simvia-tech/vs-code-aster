import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { sendTelemetry, TelemetryType } from './telemetry';
import { formatExportContent } from './ExportFormatter';
import { STATIC_MED_EXTS } from './MedEditorProvider';

interface ExportDescriptor {
  filename: string;
  content: string;
}

interface FileDescriptor {
  type: string;
  name: string;
  unit: string;
}

interface Parameters {
  time_limit: string;
  memory_limit: string;
  ncpus: string;
  mpi_nbcpu: string;
  mpi_nbnoeud: string;
}

interface FormData {
  name: string;
  parameters: Parameters;
  inputFiles: FileDescriptor[];
  outputFiles: FileDescriptor[];
}

/**
 * Result returned from the export dialog webview.
 */
export interface ExportEditorResult {
  name: string;
}

/**
 * Returns true if `filename` is a plausible match for an .export F-line
 * `type`. Types without a conventional extension (mail, base, libr, tab, nom)
 * match anything so the user can still pick arbitrary files.
 */
function matchesExportType(filename: string, type: string): boolean {
  const lower = filename.toLowerCase();
  const ext = path.extname(lower);

  if (type === 'mmed' || type === 'rmed') {
    if (STATIC_MED_EXTS.has(ext)) {
      return true;
    }
    const configured = vscode.workspace
      .getConfiguration('vs-code-aster')
      .get<string[]>('medFileExtensions', ['.med', '.mmed', '.rmed']);
    return configured.some((e) => e.toLowerCase() === ext);
  }

  if (type === 'comm') {
    return /\.com[a-z0-9]*$/.test(lower);
  }

  if (type === 'mess' || type === 'msh' || type === 'dat') {
    return ext === `.${type}`;
  }

  return true;
}

/**
 * Provides basic dialog semantics over a VS Code webview panel for export file creation and editing.
 * @template TResult The result type returned from the dialog.
 */
export class ExportEditor<TResult> implements vscode.Disposable {
  private result?: TResult;
  private destinationFolder: string;
  private deferredMessages: unknown[] = [];
  private resourceRootDir: string;
  private originalFilename?: string;

  public static async initExportEditor() {
    let exportDescriptor: ExportDescriptor = {
      filename: '',
      content: '',
    };
    let destinationFolder = undefined;

    const editor = vscode.window.activeTextEditor;

    if (editor) {
      const filePath = editor.document.uri.fsPath;
      let fileName = path.basename(filePath);
      let fileDir = path.dirname(filePath);
      if (fileName.toLowerCase().includes('.export')) {
        exportDescriptor.filename = fileName;
        exportDescriptor.content = fs.readFileSync(filePath, 'utf8');
        destinationFolder = fileDir;
      }
    }
    const testDir = path.resolve(__dirname, '..');

    const d = new ExportEditor<ExportEditorResult>(
      'export-editor-webview',
      testDir,
      'webviews/export/dist/index.html',
      exportDescriptor,
      destinationFolder,
      undefined
    );

    const result: ExportEditorResult | null = await d.getResult();

    if (result) {
      vscode.window.showInformationMessage(
        'File has been created in ' + path.basename(d.destinationFolder) + '/'
      );
    }

    d.dispose();
  }

  public readonly panel: vscode.WebviewPanel;
  public get webview(): vscode.Webview {
    return this.panel.webview;
  }

  public constructor(
    viewType: string,
    resourceRootDir: string,
    htmlFileName: string,
    exportData: ExportDescriptor,
    destinationFolder?: string,
    viewColumn?: vscode.ViewColumn
  ) {
    viewColumn = viewColumn || vscode.ViewColumn.Beside;
    this.resourceRootDir = resourceRootDir;
    const options: vscode.WebviewOptions | vscode.WebviewPanelOptions = {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: [vscode.Uri.file(resourceRootDir)],
    };

    if (destinationFolder) {
      this.destinationFolder = destinationFolder;
    } else {
      this.destinationFolder = vscode.workspace.workspaceFolders?.[0].uri.fsPath || __dirname;
    }

    const htmlFilePath = path.join(resourceRootDir, htmlFileName);
    let html = fs.readFileSync(htmlFilePath, { encoding: 'utf8' });

    const isEditing = Boolean(exportData.filename);
    const baseName = isEditing ? exportData.filename.replace(/\.export$/i, '') : '';
    const title = isEditing ? baseName : 'untitled';
    if (isEditing) {
      this.originalFilename = exportData.filename;
    }

    this.panel = vscode.window.createWebviewPanel(viewType, title, viewColumn, options);

    const editIcon = vscode.Uri.file(
      path.join(resourceRootDir, 'media', 'images', 'icone-edit.svg')
    );
    this.panel.iconPath = { light: editIcon, dark: editIcon };

    html = this.preprocessWebviewHtml(html, path.dirname(htmlFilePath));
    this.panel.webview.html = html;

    // Defer initial messages until the webview signals it is ready.
    // Without this, messages posted during construction race the webview's
    // async module load and get dropped.
    this.deferredMessages.push({
      command: 'assets',
      mode: isEditing ? 'edit' : 'create',
      originalName: baseName,
      simviaLogoUrl: this.resourceUri('media/images/simvia.svg'),
      simviaLogoDarkUrl: this.resourceUri('media/images/simvia-white.svg'),
      asterLogoUrl: this.resourceUri('media/images/code-aster.svg'),
      asterLogoDarkUrl: this.resourceUri('media/images/code-aster-white.svg'),
    });

    if (exportData.filename && exportData.content) {
      const formData = this.parseExportFile(exportData);

      const parameters = Object.values(formData.parameters);
      const inputFiles = Object.values(formData.inputFiles);
      const outputFiles = Object.values(formData.outputFiles);

      if (
        parameters.some((value) => value !== '') ||
        inputFiles.length > 0 ||
        outputFiles.length > 0
      ) {
        this.deferredMessages.push({
          command: 'exportFileAlreadyDefined',
          formData,
        });
      }
    }

    this.panel.webview.onDidReceiveMessage((message) => {
      if (message.command === 'ready') {
        for (const msg of this.deferredMessages) {
          void this.panel.webview.postMessage(msg);
        }
        this.deferredMessages = [];
      } else if (message.command === 'titleChange') {
        const name = String(message.name ?? '').trim();
        this.panel.title = name || 'untitled';
      } else if (message.command === 'cancel') {
        this.panel.dispose();
      } else if (message.command === 'wrongCreation') {
        vscode.window.showInformationMessage(`${message.value}`);
      } else if (message.command === 'result') {
        this.result = message.value as TResult;
        const lines = message.value.split('\n');
        const filename = lines[0];
        const rawContent = lines.slice(1).join('\n');
        const content = formatExportContent(rawContent, path.basename(filename));
        const fullPath = path.join(this.destinationFolder, filename);
        fs.mkdirSync(path.dirname(fullPath), { recursive: true });
        fs.writeFileSync(fullPath, content, 'utf8');
        let renamedFrom: string | undefined;
        if (this.originalFilename && this.originalFilename !== filename) {
          const oldPath = path.join(this.destinationFolder, this.originalFilename);
          renamedFrom = oldPath;
          try {
            fs.unlinkSync(oldPath);
          } catch {
            // old file may have been deleted externally; ignore
          }
        }

        void sendTelemetry(TelemetryType.EXPORT_SAVED);

        void this.revealExportFile(fullPath, renamedFrom);
        this.panel.dispose();
      } else if (message.command === 'autocomplete') {
        const suggestions = this.getMatchingFiles(message.value, message.type);
        if (suggestions.length !== 0) {
          void this.panel.webview.postMessage({
            command: 'autocompleteResult',
            suggestions,
          });
        } else {
          void this.panel.webview.postMessage({
            command: 'autocompleteFailed',
            suggestions,
          });
        }
      }
    });
  }

  private resourceUri(relativePath: string): string {
    const fullPath = path.join(this.resourceRootDir, relativePath);
    return this.webview.asWebviewUri(vscode.Uri.file(fullPath)).toString();
  }

  /**
   * Open the saved `.export` file in a text editor, reusing an existing tab
   * when the file is already open. If the file was renamed, the stale tab
   * for the old path is closed first so we don't leave a dangling editor.
   */
  private async revealExportFile(newPath: string, renamedFrom?: string): Promise<void> {
    if (renamedFrom) {
      const staleTabs: vscode.Tab[] = [];
      for (const group of vscode.window.tabGroups.all) {
        for (const tab of group.tabs) {
          if (tab.input instanceof vscode.TabInputText && tab.input.uri.fsPath === renamedFrom) {
            staleTabs.push(tab);
          }
        }
      }
      if (staleTabs.length > 0) {
        await vscode.window.tabGroups.close(staleTabs);
      }
    }
    await vscode.window.showTextDocument(vscode.Uri.file(newPath));
  }

  private getMatchingFiles(partial: string, type: string): string[] {
    if (!this.destinationFolder) {
      return [];
    }
    const allFiles = fs.readdirSync(this.destinationFolder);
    const needle = partial.toLowerCase();
    return allFiles
      .filter((name) => name !== '.vs-code-aster')
      .filter((name) => matchesExportType(name, type))
      .filter((name) => name.toLowerCase().includes(needle));
  }

  /** Parse the content of an export file into structured form data. */
  private parseExportFile(exportDescriptor: ExportDescriptor): FormData {
    let formData: FormData = {
      name: '',
      parameters: {
        time_limit: '',
        memory_limit: '',
        ncpus: '',
        mpi_nbcpu: '',
        mpi_nbnoeud: '',
      },
      inputFiles: [],
      outputFiles: [],
    };
    formData.name = exportDescriptor.filename;

    const lines = exportDescriptor.content.split('\n');

    for (const line of lines) {
      const cleanLine = line.split('#')[0].trim();
      if (!cleanLine) {
        continue;
      }

      const tokens = cleanLine.split(/\s+/);

      if (tokens[0] === 'P' && tokens.length === 3) {
        const [, key, value] = tokens;
        if (key in formData.parameters) {
          formData.parameters[key as keyof Parameters] = value;
        }
      }

      if (tokens[0] === 'F' && tokens.length === 5) {
        const [, type, name, ioFlag, unit] = tokens;
        const fileObj: FileDescriptor = {
          type: type,
          name: name,
          unit: unit,
        };
        if (ioFlag === 'D') {
          formData.inputFiles.push(fileObj);
        } else if (ioFlag === 'R') {
          formData.outputFiles.push(fileObj);
        }
      }
    }

    return formData;
  }

  private extractHtmlTitle(html: string, defaultTitle: string): string {
    const titleMatch = /<title>([^<]*)<\/title>/.exec(html);
    const title = (titleMatch && titleMatch[1]) || defaultTitle;
    return title;
  }

  /**
   * Rewrites href/src attributes relative to the HTML file so that Vite-built
   * assets (emitted as `./assets/...`) and other local resources resolve to
   * valid webview URIs. Also replaces `${webview.cspSource}` placeholders.
   */
  private preprocessWebviewHtml(html: string, htmlDir: string): string {
    html = html.replace(
      /(<link[^>]+?href="|<script[^>]+?src="|<img[^>]+?src=")([^"]+?)"/g,
      (_match, p1, p2) => {
        const resourceFullPath = path.join(htmlDir, p2);
        const uri = this.webview.asWebviewUri(vscode.Uri.file(resourceFullPath));
        return `${p1}${uri.toString()}"`;
      }
    );

    html = html.replace(/\${webview.cspSource}/g, this.webview.cspSource);

    return html;
  }

  public async getResult(cancellation?: vscode.CancellationToken): Promise<TResult | null> {
    const disposePromise = new Promise<void>((resolve) => {
      this.panel.onDidDispose(resolve);
    });

    let cancellationRegistration: vscode.Disposable | undefined;
    if (cancellation) {
      cancellationRegistration = cancellation.onCancellationRequested(() => {
        this.panel.dispose();
      });
    }

    await disposePromise;

    if (cancellationRegistration) {
      cancellationRegistration.dispose();
    }

    return this.result === undefined ? null : this.result;
  }

  public dispose() {
    this.panel.dispose();
  }
}
