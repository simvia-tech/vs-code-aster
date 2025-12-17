import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

/**
 * Provides basic dialog semantics over a VS Code webview panel for mesh visualization.
 */
export class WebviewVisu implements vscode.Disposable {
  public readonly panel: vscode.WebviewPanel;

  private groups?: string[];
  private selectedGroups: string[];

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
   */
  public constructor(
    viewType: string,
    resourceRootDir: string,
    htmlFileName: string,
    fileContexts: string[],
    objFilenames: string[],
    viewColumn?: vscode.ViewColumn
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

    // Extract title from HTML file
    let htmlFileContent = fs.readFileSync(htmlFilePath, { encoding: "utf8" });
    const title = this.extractHtmlTitle(htmlFileContent, "Visualizer");

    // Create webview panel with icon
    this.panel = vscode.window.createWebviewPanel(
      viewType,
      title,
      viewColumn,
      options
    );
    this.panel.iconPath = vscode.Uri.file(
      path.join(resourceRootDir, "resources", "icons", "3d.svg")
    );
    console.log("[WebviewVisu] Webview panel created");

    // Set HTML content for the webview
    const html = this.preprocessWebviewHtml(this.panel, htmlFilePath);
    this.panel.webview.html = html;
    console.log("[WebviewVisu] HTML content set in webview");

    // Initialize selectedGroups
    this.selectedGroups = [];

    // Listen for messages from the webview
    this.panel.webview.onDidReceiveMessage((e) => {
      switch (e.type) {
        case "ready":
          // Webview is ready, send initialization message
          console.log("[WebviewVisu] Webview ready signal received");
          if (objFilenames) {
            console.log("[WebviewVisu] Sending init with files:", objFilenames);
            this.panel.webview.postMessage({
              type: "init",
              body: { fileContexts, objFilenames },
            });
          }
          break;
        case "debugPanel":
          // Log debug messages from the webview
          console.log("[WebviewVisu] Message received from webview:", e.text);
          break;
        case "groups":
          // Receive the list of groups from the webview and store it
          let groupList = e.groupList;
          console.log("Group list : ", groupList);
          this.groups = groupList;
          this.panel.webview.postMessage({
            type: "addGroupButtons",
            body: { groupList },
          });
          break;
        default:
          console.warn("[WebviewVisu] Unknown message type:", e.type);
      }
    });

    // Dispose the webview panel when it is closed
    this.panel.onDidDispose(() => {
      console.log("[WebviewVisu] Webview panel disposed");
      this.dispose();
    }, null);

    console.log("[WebviewVisu] Constructor finished");
  }

  /**
   * Display or hide groups in the webview based on the provided text.
   * Groups present in the text will be displayed; others will be hidden.
   * @param text The text to check for group names.
   */
  public showGroupsFromTextSelection(text: string) {
    if (!this.panel) {
      return;
    }

    // Parse the text to find group names
    const readGroups =
      this.groups?.filter((groupName) => {
        const regex = new RegExp(
          `\\b${groupName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`
        );
        return regex.test(text);
      }) || [];

    // Hide groups that are no longer in the text
    this.selectedGroups = this.selectedGroups.filter((oldGroup) => {
      if (!readGroups.includes(oldGroup)) {
        console.log("Hide group:", oldGroup);
        this.panel.webview.postMessage({
          type: "displayGroup",
          body: { group: oldGroup, visible: false },
        });
        return false;
      }
      return true;
    });

    // Show groups that are new to the text
    readGroups.forEach((group) => {
      if (!this.selectedGroups.includes(group)) {
        console.log("Display group:", group);
        this.panel.webview.postMessage({
          type: "displayGroup",
          body: { group, visible: true },
        });
        this.selectedGroups.push(group);
      }
    });
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
  private preprocessWebviewHtml(
    panel: vscode.WebviewPanel,
    htmlFilePath: string
  ): string {
    let html = fs.readFileSync(htmlFilePath, { encoding: "utf8" });

    const htmlDir = path.dirname(htmlFilePath);

    // Replace relative paths (href/src/img) with valid URIs for the webview
    html = html.replace(
      /(<link.+?href="|<script.+?src="|<img.+?src=")(.+?)"/g,
      (match, p1, p2) => {
        const resourceFullPath = path.join(htmlDir, p2);
        const uri = panel.webview.asWebviewUri(
          vscode.Uri.file(resourceFullPath)
        );
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
