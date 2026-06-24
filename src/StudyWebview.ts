import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { StudySpec } from './scenario/spec';
import { MeshGroups } from './MeshGroups';
import { pickMeshFile, readGroups, writeStudy } from './studyFiles';

interface WebviewMessage {
  command: string;
  name?: string;
  spec?: StudySpec;
}

/**
 * Host controller for the "Generate study from scenario" webview. Owns the
 * panel lifecycle and shuttles data to/from the Svelte form. The form builds
 * the StudySpec client-side (and previews it in-pane); the host only reads the
 * mesh groups, runs the file dialog, and writes the result. Modeled on
 * src/ExportEditor.ts.
 */
export class StudyWebview {
  private readonly panel: vscode.WebviewPanel;
  private readonly resourceRootDir: string;
  private deferredMessages: unknown[] = [];
  private medPath: string;

  static show(medPath: string, groups: MeshGroups, groupsAvailable: boolean): StudyWebview {
    return new StudyWebview(medPath, groups, groupsAvailable);
  }

  private constructor(medPath: string, groups: MeshGroups, groupsAvailable: boolean) {
    this.medPath = medPath;
    this.resourceRootDir = path.resolve(__dirname, '..');

    const options: vscode.WebviewOptions & vscode.WebviewPanelOptions = {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: [vscode.Uri.file(this.resourceRootDir)],
    };

    this.panel = vscode.window.createWebviewPanel(
      'study-generator-webview',
      'New study',
      // Open as a full editor tab in the active group (not a side-by-side
      // split). VS Code webviews are always editor tabs — there is no floating
      // popup API — so this is the "full size by default" behavior.
      vscode.ViewColumn.Active,
      options
    );

    const icon = vscode.Uri.file(
      path.join(this.resourceRootDir, 'media', 'images', 'icone-wand.svg')
    );
    this.panel.iconPath = { light: icon, dark: icon };

    const htmlFilePath = path.join(this.resourceRootDir, 'webviews/study/dist/index.html');
    let html = fs.readFileSync(htmlFilePath, { encoding: 'utf8' });
    html = this.preprocessWebviewHtml(html, path.dirname(htmlFilePath));
    this.panel.webview.html = html;

    // Defer init until the webview signals 'ready' (avoids racing module load).
    this.deferredMessages.push({
      command: 'init',
      meshFileName: path.basename(medPath),
      groups,
      groupsAvailable,
      simviaLogoUrl: this.resourceUri('media/images/simvia.svg'),
      simviaLogoDarkUrl: this.resourceUri('media/images/simvia-white.svg'),
      asterLogoUrl: this.resourceUri('media/images/code-aster.svg'),
      asterLogoDarkUrl: this.resourceUri('media/images/code-aster-white.svg'),
    });

    this.panel.webview.onDidReceiveMessage((message: WebviewMessage) =>
      this.handleMessage(message)
    );
  }

  private async handleMessage(message: WebviewMessage): Promise<void> {
    switch (message.command) {
      case 'ready':
        for (const msg of this.deferredMessages) {
          void this.panel.webview.postMessage(msg);
        }
        this.deferredMessages = [];
        break;
      case 'titleChange':
        this.panel.title = String(message.name ?? '').trim() || 'New study';
        break;
      case 'cancel':
        this.panel.dispose();
        break;
      case 'submit':
        if (message.spec) {
          await writeStudy(message.spec, this.medPath);
          this.panel.dispose();
        }
        break;
      case 'browseMesh': {
        const med = await pickMeshFile();
        if (!med) {
          return;
        }
        this.medPath = med;
        const { groups, available } = await readGroups(med);
        void this.panel.webview.postMessage({
          command: 'meshChanged',
          meshFileName: path.basename(med),
          groups,
          groupsAvailable: available,
        });
        break;
      }
    }
  }

  private resourceUri(relativePath: string): string {
    const fullPath = path.join(this.resourceRootDir, relativePath);
    return this.panel.webview.asWebviewUri(vscode.Uri.file(fullPath)).toString();
  }

  /**
   * Rewrites Vite-built `./assets/...` href/src to webview URIs and replaces the
   * `${webview.cspSource}` placeholder. Identical to ExportEditor's logic.
   */
  private preprocessWebviewHtml(html: string, htmlDir: string): string {
    html = html.replace(
      /(<link[^>]+?href="|<script[^>]+?src="|<img[^>]+?src=")([^"]+?)"/g,
      (_match, p1, p2) => {
        const resourceFullPath = path.join(htmlDir, p2);
        const uri = this.panel.webview.asWebviewUri(vscode.Uri.file(resourceFullPath));
        return `${p1}${uri.toString()}"`;
      }
    );
    html = html.replace(/\$\{webview.cspSource\}/g, this.panel.webview.cspSource);
    return html;
  }
}
