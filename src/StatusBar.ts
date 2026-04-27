import * as vscode from 'vscode';
import { LspServer } from './LspServer';

interface CommandFamiliesAnalysis {
  mesh: string[];
  material: string[];
  bcAndLoads: string[];
  analysis: string[];
  output: string[];
}

/**
 * Tiny left-side status-bar nudge: a single icon, neutral when the
 * active `.comm` file already covers most of the canonical command
 * families, warning-tinted when it covers fewer than three. Click
 * focuses the sidebar's Command browser group, which is where the
 * real dictionary now lives.
 */
export class StatusBar {
  private static _instance: StatusBar | null = null;
  private statusBarItem: vscode.StatusBarItem;
  private currentAnalysis: CommandFamiliesAnalysis | null = null;
  private disposables: vscode.Disposable[] = [];

  private constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
    this.statusBarItem.command = 'vs-code-aster.commandBrowser.focus';
  }

  public static get instance(): StatusBar {
    if (!StatusBar._instance) {
      StatusBar._instance = new StatusBar();
    }
    return StatusBar._instance;
  }

  public async activate(context: vscode.ExtensionContext) {
    const editorChange = vscode.window.onDidChangeActiveTextEditor((editor) =>
      this.onEditorChange(editor)
    );
    this.disposables.push(editorChange);
    // Retry once the LSP is ready (the first analyze on activation
    // typically lands before the server is up and silently bails).
    this.disposables.push(
      LspServer.instance.onReady(() => this.onEditorChange(vscode.window.activeTextEditor))
    );
    this.onEditorChange(vscode.window.activeTextEditor);
    context.subscriptions.push(this.statusBarItem, ...this.disposables);
  }

  /** Re-analyze + render. Called after `cave use` (LSP restart) and on
   * editor-change. */
  public async onEditorChange(editor: vscode.TextEditor | undefined) {
    if (!editor || editor.document.languageId !== 'comm') {
      this.statusBarItem.hide();
      return;
    }
    this.statusBarItem.show();
    await this.analyzeDocument(editor.document);
  }

  private async analyzeDocument(document: vscode.TextDocument) {
    try {
      const client = LspServer.instance.client;
      if (!client) {
        this.statusBarItem.hide();
        return;
      }
      const analysis = await client.sendRequest<CommandFamiliesAnalysis>(
        'codeaster/analyzeCommandFamilies',
        { uri: document.uri.toString() }
      );
      this.currentAnalysis = analysis;
      this.render(analysis);
    } catch {
      // LSP may not be ready yet (e.g. first activation). Hide silently;
      // we'll re-render on the next editor / file change.
      this.statusBarItem.hide();
    }
  }

  private render(analysis: CommandFamiliesAnalysis) {
    const filled = Object.values(analysis).filter(
      (cmds) => Array.isArray(cmds) && cmds.length > 0
    ).length;
    // Warning tint only on near-empty files (0–2 families). Anything
    // with at least three families set looks "in-progress" enough.
    const isEmpty = filled < 3;
    this.statusBarItem.text = isEmpty ? '$(circle-outline)' : '$(symbol-namespace)';
    this.statusBarItem.tooltip = new vscode.MarkdownString(
      isEmpty
        ? `**code_aster:** ${filled}/5 command families used.\n\nClick to browse commands.`
        : `**code_aster:** ${filled}/5 command families used.\n\nClick to browse commands.`
    );
    this.statusBarItem.backgroundColor = isEmpty
      ? new vscode.ThemeColor('statusBarItem.warningBackground')
      : undefined;
  }

  public dispose() {
    this.statusBarItem.dispose();
    this.disposables.forEach((d) => d.dispose());
  }
}
