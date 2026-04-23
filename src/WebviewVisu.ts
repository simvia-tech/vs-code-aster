import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { getScreenshotsDir, getRecordingsDir } from './projectPaths';

/**
 * Provides basic dialog semantics over a VS Code webview panel for mesh visualization.
 */
export class WebviewVisu implements vscode.Disposable {
  public readonly panel: vscode.WebviewPanel;

  private groups?: string[];
  private objects?: string[];
  private selectedGroups: string[];

  private readyReceived = false;
  private deferredInit?: { fileContexts: string[]; objFilenames: string[] };
  public sourceDir?: string;

  public get webview(): vscode.Webview {
    return this.panel.webview;
  }

  /**
   * Constructs a new webview for mesh viewer. The visualizer is shown as soon as
   * it is constructed.
   *
   * The viewer instance may only be used once. It may not be re-shown
   * after it is closed; create another instance instead.
   *
   * Initializes the mesh viewer webview, loads HTML, sets up resource references, and handles communication with the webview.
   * The webview is shown immediately and can only be used once.
   *
   * @param viewType The type of the webview.
   * @param resourceRootDir The root directory for resources.
   * @param htmlFileName The HTML file for the mesh viewer UI.
   * @param fileContexts The file contexts to send to the webview.
   * @param objFilenames File names for mesh data.
   * @param viewColumn The column in which to show the webview.
   * @param title Optional tab title.
   * @param existingPanel Optional pre-existing panel (e.g. provided by a CustomEditorProvider).
   *   If provided, `viewColumn` is ignored and the panel is reused instead of creating a new one.
   */
  public constructor(
    viewType: string,
    resourceRootDir: string,
    htmlFileName: string,
    fileContexts: string[],
    objFilenames: string[],
    viewColumn?: vscode.ViewColumn,
    title?: string,
    existingPanel?: vscode.WebviewPanel
  ) {
    viewColumn = viewColumn || vscode.ViewColumn.Beside;

    // VS Code webview options
    const options: vscode.WebviewOptions | vscode.WebviewPanelOptions = {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: [vscode.Uri.file(resourceRootDir)],
    };

    // Get HTML file path
    const htmlFilePath = path.join(resourceRootDir, htmlFileName);

    // Use provided title or fall back to the HTML <title> tag
    if (!title) {
      const htmlFileContent = fs.readFileSync(htmlFilePath, { encoding: 'utf8' });
      title = this.extractHtmlTitle(htmlFileContent, 'Visualizer');
    }

    if (existingPanel) {
      // Reuse a panel supplied by VS Code (CustomEditorProvider flow)
      this.panel = existingPanel;
      this.panel.webview.options = {
        enableScripts: true,
        localResourceRoots: [vscode.Uri.file(resourceRootDir)],
      };
      this.panel.title = title;
    } else {
      this.panel = vscode.window.createWebviewPanel(viewType, title, viewColumn, options);
    }
    this.panel.iconPath = {
      light: vscode.Uri.file(path.join(resourceRootDir, 'media', 'images', 'icone-med.svg')),
      dark: vscode.Uri.file(path.join(resourceRootDir, 'media', 'images', 'icone-med.svg')),
    };
    console.log('[WebviewVisu] Webview panel created');

    // Set HTML content for the webview
    const html = this.preprocessWebviewHtml(this.panel, htmlFilePath);
    this.panel.webview.html = html;
    console.log('[WebviewVisu] HTML content set in webview');

    // Initialize selectedGroups
    this.selectedGroups = [];

    // Listen for messages from the webview
    this.panel.webview.onDidReceiveMessage((e) => {
      switch (e.type) {
        case 'ready':
          // Webview is ready, send initialization message
          console.log('[WebviewVisu] Webview ready signal received');
          this.readyReceived = true;
          if (objFilenames && objFilenames.length > 0) {
            console.log('[WebviewVisu] Sending init with files:', objFilenames);
            this.doSendInit(fileContexts, objFilenames);
          } else if (this.deferredInit) {
            console.log(
              '[WebviewVisu] Flushing deferred init with files:',
              this.deferredInit.objFilenames
            );
            this.doSendInit(this.deferredInit.fileContexts, this.deferredInit.objFilenames);
            this.deferredInit = undefined;
          }
          break;
        case 'saveSettings':
          // Persist viewer settings back to VS Code configuration
          const cfg = vscode.workspace.getConfiguration('vs-code-aster');
          const settingKeys = [
            'hiddenObjectOpacity',
            'edgeMode',
            'edgeThresholdMultiplier',
            'edgeGroupThickness',
            'edgeGroupDepthOffset',
            'nodeGroupSize',
            'sidebarSort',
            'groupByKind',
            'groupTransparency',
            'showOrientationWidget',
            'showBoundingBox',
            'showWireframe',
            'dreamBackground',
            'autoRotate',
            'autoRotateSpeed',
            'autoRotateReverse',
          ];
          for (const key of settingKeys) {
            if (e.settings[key] !== undefined) {
              cfg.update(`viewer.${key}`, e.settings[key], vscode.ConfigurationTarget.Global);
            }
          }
          break;
        case 'saveScreenshot': {
          if (this.sourceDir) {
            const base64 = (e.dataUrl as string).replace(/^data:image\/png;base64,/, '');
            const buffer = Buffer.from(base64, 'base64');
            const screenshotsDir = getScreenshotsDir(this.sourceDir);
            const filePath = path.join(screenshotsDir, e.filename as string);
            fs.writeFileSync(filePath, buffer);
          }
          break;
        }
        case 'saveRecording': {
          if (this.sourceDir) {
            const dataUrl = e.dataUrl as string;
            const commaIdx = dataUrl.indexOf(';base64,');
            const base64 = commaIdx >= 0 ? dataUrl.slice(commaIdx + ';base64,'.length) : dataUrl;
            const buffer = Buffer.from(base64, 'base64');
            const recordingsDir = getRecordingsDir(this.sourceDir);
            const filePath = path.join(recordingsDir, e.filename as string);
            fs.writeFileSync(filePath, buffer);
          }
          break;
        }
        case 'debugPanel':
          // Log debug messages from the webview
          console.log('[WebviewVisu] Message received from webview:', e.text);
          break;
        case 'groups':
          // Receive the list of groups from the webview and store it
          let groupList = e.groupList;
          console.log('Group list : ', groupList);
          this.groups = groupList;
          this.objects = e.objectList;
          this.panel.webview.postMessage({
            type: 'addGroupButtons',
            body: { groupList },
          });
          break;
        default:
          console.warn('[WebviewVisu] Unknown message type:', e.type);
      }
    });

    // Dispose the webview panel when it is closed
    this.panel.onDidDispose(() => {
      console.log('[WebviewVisu] Webview panel disposed');
      this.dispose();
    }, null);

    console.log('[WebviewVisu] Constructor finished');
  }

  /**
   * Send init data to the webview. If the webview has already signalled `ready`,
   * posts the message immediately; otherwise buffers the data so it is sent
   * when `ready` fires.
   *
   * Used by the standalone .med editor provider, which only has obj data
   * available after running conversion asynchronously.
   */
  public sendInit(fileContexts: string[], objFilenames: string[]): void {
    if (this.readyReceived) {
      this.doSendInit(fileContexts, objFilenames);
    } else {
      this.deferredInit = { fileContexts, objFilenames };
    }
  }

  private doSendInit(fileContexts: string[], objFilenames: string[]): void {
    const config = vscode.workspace.getConfiguration('vs-code-aster');
    const settings = {
      hiddenObjectOpacity: config.get<number>('viewer.hiddenObjectOpacity', 0),
      edgeMode: config.get<string>('viewer.edgeMode', 'threshold'),
      edgeThresholdMultiplier: config.get<number>('viewer.edgeThresholdMultiplier', 1),
      edgeGroupThickness: config.get<number>('viewer.edgeGroupThickness', 3),
      edgeGroupDepthOffset: config.get<boolean>('viewer.edgeGroupDepthOffset', true),
      nodeGroupSize: config.get<number>('viewer.nodeGroupSize', 1),
      sidebarSort: config.get<string>('viewer.sidebarSort', 'natural'),
      groupByKind: config.get<boolean>('viewer.groupByKind', true),
      groupTransparency: config.get<number>('viewer.groupTransparency', 0.2),
      showOrientationWidget: config.get<boolean>('viewer.showOrientationWidget', true),
      showBoundingBox: config.get<boolean>('viewer.showBoundingBox', false),
      showWireframe: config.get<boolean>('viewer.showWireframe', false),
      dreamBackground: config.get<boolean>('viewer.dreamBackground', true),
      autoRotate: config.get<boolean>('viewer.autoRotate', false),
      autoRotateSpeed: config.get<number>('viewer.autoRotateSpeed', 15),
      autoRotateReverse: config.get<boolean>('viewer.autoRotateReverse', false),
    };
    this.panel.webview.postMessage({
      type: 'init',
      body: { fileContexts, objFilenames, settings },
    });
  }

  /**
   * Display or hide groups in the webview based on the provided text.
   * Groups present in the text will be displayed; others will be hidden.
   * @param text The text to check for group names.
   */
  private makeWholeTokenRegex(name: string): RegExp {
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return new RegExp(`(?<![a-zA-Z0-9_-])${escaped}(?![a-zA-Z0-9_-])`);
  }

  public showGroupsFromTextSelection(text: string) {
    if (!this.panel) {
      return;
    }

    // Parse the text to find group names
    // Group keys are like "all_mesh.obj::SURFACE_1::type"; match against the short name only
    const readGroups =
      this.groups?.filter((groupName) => {
        const shortName = groupName.includes('::') ? groupName.split('::')[1]! : groupName;
        return this.makeWholeTokenRegex(shortName).test(text);
      }) || [];

    // Hide groups that are no longer in the text
    this.selectedGroups = this.selectedGroups.filter((oldGroup) => {
      if (!readGroups.includes(oldGroup)) {
        this.panel.webview.postMessage({
          type: 'displayGroup',
          body: { group: oldGroup, visible: false },
        });
        return false;
      }
      return true;
    });

    // Show groups that are new to the text
    readGroups.forEach((group) => {
      if (!this.selectedGroups.includes(group)) {
        this.panel.webview.postMessage({
          type: 'displayGroup',
          body: { group, visible: true },
        });
        this.selectedGroups.push(group);
      }
    });

    // Parse the text to find object names
    // Object keys are like "all_mesh.obj"; match against the stem (no "all_" prefix, no extension)
    // Only send showOnlyObjects when a mesh name is explicitly selected, to avoid
    // resetting user-hidden meshes on every text selection change.
    const selectedObjects =
      this.objects?.filter((objectKey) => {
        const withoutPrefix = objectKey.startsWith('all_') ? objectKey.slice(4) : objectKey;
        const shortName = withoutPrefix.replace(/\.[^.]+$/, '');
        return this.makeWholeTokenRegex(shortName).test(text);
      }) || [];

    if (selectedObjects.length > 0) {
      this.panel.webview.postMessage({
        type: 'showOnlyObjects',
        body: { objects: selectedObjects },
      });
    }
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
   * Preprocess the HTML content for the webview by adjusting resource paths and placeholders.
   * @param panel The webview panel.
   * @param htmlFilePath The path to the HTML file.
   * @returns The preprocessed HTML content as a string.
   */
  private preprocessWebviewHtml(panel: vscode.WebviewPanel, htmlFilePath: string): string {
    let html = fs.readFileSync(htmlFilePath, { encoding: 'utf8' });

    const htmlDir = path.dirname(htmlFilePath);

    // Replace relative paths (href/src/img) with valid URIs for the webview
    html = html.replace(
      /(<link.+?href="|<script.+?src="|<img.+?src=")(.+?)"/g,
      (_match, p1, p2) => {
        const resourceFullPath = path.join(htmlDir, p2);
        const uri = panel.webview.asWebviewUri(vscode.Uri.file(resourceFullPath));
        return `${p1}${uri.toString()}"`;
      }
    );

    html = html.replace(/\${webview.cspSource}/g, panel.webview.cspSource);

    return html;
  }

  public dispose() {
    this.panel.dispose();
  }
}
