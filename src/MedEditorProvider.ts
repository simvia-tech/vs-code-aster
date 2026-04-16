/**
 * Custom editor provider for MED mesh files.
 *
 * Registers as the default editor for `.med`, `.mmed`, `.rmed` via the
 * `customEditors` contribution in package.json. When VS Code opens one of
 * those files, it calls `resolveCustomEditor` and hands us a WebviewPanel,
 * which we populate with the same mesh viewer used by the .comm flow.
 *
 * This bypasses the "binary file" message that VS Code would otherwise show
 * when the user clicks a .med file.
 */
import * as vscode from 'vscode';
import * as path from 'path';
import { getObjFiles, readObjFilesContent } from './VisuManager';
import { WebviewVisu } from './WebviewVisu';
import { sendTelemetry, TelemetryType } from './telemetry';

/**
 * MED extensions that are routed to the custom editor via the static
 * `customEditors` selector in package.json.
 *
 * User-configured numeric extensions (e.g. `.71`, `.72`) are not listed here
 * and are handled by the dynamic interception in `extension.ts`.
 */
export const STATIC_MED_EXTS = new Set(['.med', '.mmed', '.rmed']);

export class MedEditorProvider implements vscode.CustomReadonlyEditorProvider<vscode.CustomDocument> {
  public static readonly viewType = 'vs-code-aster.medViewer';

  /** Active standalone viewers, keyed by the MED file's fsPath. */
  private activeViewers: Map<string, WebviewVisu> = new Map();

  private constructor(private readonly extensionRootDir: string) {}

  /**
   * Register the provider with VS Code. Returns a Disposable that should be
   * pushed onto `context.subscriptions`.
   */
  public static register(context: vscode.ExtensionContext): vscode.Disposable {
    const provider = new MedEditorProvider(context.extensionUri.fsPath);
    return vscode.window.registerCustomEditorProvider(MedEditorProvider.viewType, provider, {
      webviewOptions: {
        retainContextWhenHidden: true,
      },
      supportsMultipleEditorsPerDocument: false,
    });
  }

  async openCustomDocument(
    uri: vscode.Uri,
    _openContext: vscode.CustomDocumentOpenContext,
    _token: vscode.CancellationToken
  ): Promise<vscode.CustomDocument> {
    return { uri, dispose: () => {} };
  }

  async resolveCustomEditor(
    document: vscode.CustomDocument,
    webviewPanel: vscode.WebviewPanel,
    _token: vscode.CancellationToken
  ): Promise<void> {
    const medUri = document.uri;
    const medPath = medUri.fsPath;
    const medBaseName = path.basename(medPath, path.extname(medPath));

    // Build the viewer with an empty initial payload so the loading screen
    // appears immediately. Real data is sent via `sendInit` after conversion.
    const visu = new WebviewVisu(
      MedEditorProvider.viewType,
      this.extensionRootDir,
      'webviews/viewer/dist/index.html',
      [],
      [],
      undefined,
      medBaseName,
      webviewPanel
    );

    visu.sourceDir = path.dirname(medPath);
    this.activeViewers.set(medPath, visu);
    webviewPanel.onDidDispose(() => {
      this.activeViewers.delete(medPath);
    });

    void sendTelemetry(TelemetryType.VIEWER_OPENED);

    try {
      const objUris = await getObjFiles([medPath]);

      if (objUris.length === 0) {
        webviewPanel.webview.postMessage({
          type: 'error',
          body: {
            message: `Failed to convert ${path.basename(medPath)} to a viewable format.`,
          },
        });
        return;
      }

      const fileContexts = await readObjFilesContent(objUris);
      const objFilenames = objUris.map((uri) => path.basename(uri.fsPath));
      visu.sendInit(fileContexts, objFilenames);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      webviewPanel.webview.postMessage({
        type: 'error',
        body: { message },
      });
    }
  }
}
