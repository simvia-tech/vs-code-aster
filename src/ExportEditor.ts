import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import { sendTelemetry, TelemetryType } from "./telemetry";

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
 * Provides basic dialog semantics over a VS Code webview panel for export file creation and editing.
 * @template TResult The result type returned from the dialog.
 */
export class ExportEditor<TResult> implements vscode.Disposable {
  private result?: TResult;
  private destinationFolder: string;

  public static async initExportEditor() {
    let exportDescriptor: ExportDescriptor = {
      filename: "",
      content: "",
    };
    let destinationFolder = undefined;

    const editor = vscode.window.activeTextEditor;

    if (editor) {
      const filePath = editor.document.uri.fsPath;
      let fileName = path.basename(filePath);
      let fileDir = path.dirname(filePath);
      if (fileName.toLowerCase().includes(".export")) {
        exportDescriptor.filename = fileName;
        exportDescriptor.content = fs.readFileSync(filePath, "utf8");
        destinationFolder = fileDir;
      }
    }
    const testDir = path.resolve(__dirname, "..");

    const d = new ExportEditor<ExportEditorResult>(
      "export-editor-webview",
      testDir,
      "resources/export_form/export.html",
      exportDescriptor,
      destinationFolder,
      undefined
    );

    const result: ExportEditorResult | null = await d.getResult();

    if (result) {
      vscode.window.showInformationMessage(
        "File has been created in " + path.basename(d.destinationFolder) + "/"
      );
    }

    d.dispose();
  }

  public readonly panel: vscode.WebviewPanel;
  public get webview(): vscode.Webview {
    return this.panel.webview;
  }

  /**
   * Initializes the export webview, loads HTML, sets up resource references, and handles export file logic.
   * The panel is shown immediately and can only be used once.
   *
   * @param viewType The type of the webview.
   * @param resourceRootDir The root directory for resources.
   * @param htmlFileName The HTML file for the UI.
   * @param viewColumn The column in which to show the webview.
   * @param exportFilename Optional export file to pre-fill the webview.
   */
  public constructor(
    viewType: string,
    resourceRootDir: string,
    htmlFileName: string,
    exportData: ExportDescriptor,
    destinationFolder?: string,
    viewColumn?: vscode.ViewColumn
  ) {
    viewColumn = viewColumn || vscode.ViewColumn.Beside;
    const options: vscode.WebviewOptions | vscode.WebviewPanelOptions = {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.file(resourceRootDir)],
    };

    if (destinationFolder) {
      this.destinationFolder = destinationFolder;
    } else {
      this.destinationFolder =
        vscode.workspace.workspaceFolders?.[0].uri.fsPath || __dirname;
    }

    const htmlFile = path.join(resourceRootDir, htmlFileName);
    let html = fs.readFileSync(htmlFile, { encoding: "utf8" });

    const title = this.extractHtmlTitle(html, "Export Editor");

    this.panel = vscode.window.createWebviewPanel(
      viewType,
      title,
      viewColumn,
      options
    );

    html = this.fixResourceReferences(html, resourceRootDir);
    html = this.fixCspSourceReferences(html);
    this.panel.webview.html = html;

    // If an export file is found, parse and fill the form in the webview
    // const exportData = this.exportFile();
    if (exportData.filename && exportData.content) {
      const formData = this.parseExportFile(exportData);

      const parameters = Object.values(formData.parameters);
      const inputFiles = Object.values(formData.inputFiles);
      const outputFiles = Object.values(formData.outputFiles);

      if (
        parameters.some((value) => value !== "") ||
        inputFiles.length > 0 ||
        outputFiles.length > 0
      ) {
        this.panel.webview.postMessage({
          command: "exportFileAlreadyDefined",
          formData,
        });
      }
    }

    const files = this.getMatchingFiles("", "");
    this.panel.webview.postMessage({ command: "verifyFileNames", files });

    this.panel.webview.onDidReceiveMessage((message) => {
      if (message.command === "cancel") {
        this.panel.dispose();
      } else if (message.command === "wrongCreation") {
        vscode.window.showInformationMessage(`${message.value}`);
      } else if (message.command === "result") {
        this.result = message.value as TResult;
        const lines = message.value.split("\n");
        const filename = lines[0];
        const content = lines.slice(1).join("\n");
        const fullPath = path.join(this.destinationFolder, filename);
        fs.writeFileSync(fullPath, content, "utf8");

        // Report telemetry that an export file was created/saved
        void sendTelemetry(TelemetryType.EXPORT_SAVED);

        this.panel.dispose();
      } else if (message.command === "autocomplete") {
        const suggestions = this.getMatchingFiles(message.value, message.type);
        if (suggestions.length !== 0) {
          this.panel.webview.postMessage({
            command: "autocompleteResult",
            suggestions,
          });
        } else {
          this.panel.webview.postMessage({
            command: "autocompleteFailed",
            suggestions,
          });
        }
      }
    });
  }

  private getMatchingFiles(partial: string, type: string): string[] {
    if (!this.destinationFolder) {
      return [];
    }
    const allFiles = fs.readdirSync(this.destinationFolder);
    return allFiles.filter((name) =>
      name.toLowerCase().includes(partial.toLowerCase())
    );
  }

  /** * Parse the content of an export file into structured form data.
   * @param exportDescriptor The export file descriptor containing filename and content.
   * @returns The parsed form data including parameters and file descriptors.
   */
  private parseExportFile(exportDescriptor: ExportDescriptor): FormData {
    let formData: FormData = {
      name: "",
      parameters: {
        time_limit: "",
        memory_limit: "",
        ncpus: "",
        mpi_nbcpu: "",
        mpi_nbnoeud: "",
      },
      inputFiles: [],
      outputFiles: [],
    };
    formData.name = exportDescriptor.filename;

    const lines = exportDescriptor.content.split("\n");

    for (const line of lines) {
      const cleanLine = line.split("#")[0].trim();
      if (!cleanLine) {
        continue;
      }

      const tokens = cleanLine.split(/\s+/);

      if (tokens[0] === "P" && tokens.length === 3) {
        const [_, key, value] = tokens;
        if (key in formData.parameters) {
          formData.parameters[key as keyof Parameters] = value;
        }
      }

      if (tokens[0] === "F" && tokens.length === 5) {
        const [_, type, name, ioFlag, unit] = tokens;
        const fileObj: FileDescriptor = {
          type: type,
          name: name,
          unit: unit,
        };
        if (ioFlag === "D") {
          formData.inputFiles.push(fileObj);
        } else if (ioFlag === "R") {
          formData.outputFiles.push(fileObj);
        }
      }
    }

    return formData;
  }

  /**
   * Extract the dialog title from the <title> tag of the HTML.
   */
  private extractHtmlTitle(html: string, defaultTitle: string): string {
    const titleMatch = /\<title\>([^<]*)\<\/title\>/.exec(html);
    const title = (titleMatch && titleMatch[1]) || defaultTitle;
    return title;
  }

  /**
   * Replace references to href="./file" or src="./file" with VS Code resource URIs.
   */
  private fixResourceReferences(html: string, resourceRootDir: string): string {
    const refRegex = /((href)|(src))="(\.\/[^"]+)"/g;
    let refMatch;
    while ((refMatch = refRegex.exec(html)) !== null) {
      const offset = refMatch.index;
      const length = refMatch[0].length;
      const refAttr = refMatch[1];
      const refName = refMatch[4];
      const refPath = path.join(resourceRootDir, refName);
      const refUri = this.webview.asWebviewUri(vscode.Uri.file(refPath));
      const refReplace = refAttr + '="' + refUri + '"';
      html = html.slice(0, offset) + refReplace + html.slice(offset + length);
    }
    return html;
  }

  /**
   * Replace references to ${webview.cspSource} with the actual value.
   */
  private fixCspSourceReferences(html: string): string {
    const cspSourceRegex = /\${webview.cspSource}/g;
    let cspSourceMatch;
    while ((cspSourceMatch = cspSourceRegex.exec(html)) !== null) {
      html =
        html.slice(0, cspSourceMatch.index) +
        this.webview.cspSource +
        html.slice(cspSourceMatch.index + cspSourceMatch[0].length);
    }

    return html;
  }

  /**
   * Waits for the dialog to close, then gets the result, or `null`
   * if the dialog was cancelled.
   * @param cancellation Optional cancellation token that can be used to
   * cancel waiting on a result. Cancelling the token also closes the dialog.
   */
  public async getResult(
    cancellation?: vscode.CancellationToken
  ): Promise<TResult | null> {
    const disposePromise = new Promise<void>((resolve, reject) => {
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
