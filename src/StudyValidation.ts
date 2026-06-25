/**
 * "Validate Current Study" command.
 *
 * Resolves the active study (a `.comm` plus its associated `.export`), asks
 * the Python LSP to validate it as a whole, then surfaces the result in two
 * places: a dedicated `DiagnosticCollection` (Problems panel) and the
 * `webviews/validation` Svelte report. See `python/lsp/validation_manager.py`
 * for the analysis and `src/validationReport.ts` for the shared report types.
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { LspServer } from './LspServer';
import { commNameFromExport, exportReferencesComm } from './studyResolution';
import { ValidationReport, ValidationDiagnostic } from './validationReport';

interface ResolvedStudy {
  commUri: vscode.Uri;
  commText: string;
  exportUri?: vscode.Uri;
  exportText?: string;
}

let diagnosticCollection: vscode.DiagnosticCollection | undefined;
let reportPanel: vscode.WebviewPanel | undefined;
// The study the report panel currently shows. The panel is reused across
// runs, so the "jump to line" handler reads this rather than capturing one
// study in its closure.
let currentStudy: ResolvedStudy | undefined;
// Extension root, captured at registration, so the report panel can resolve
// its built webview assets and tab icon on disk.
let extensionUri: vscode.Uri | undefined;
// The Svelte webview signals `ready` once mounted; until then we hold the
// init message (the panel may still be loading on the first run).
let webviewReady = false;
let pendingInit: unknown | undefined;

function getDiagnosticCollection(): vscode.DiagnosticCollection {
  if (!diagnosticCollection) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('code_aster study');
  }
  return diagnosticCollection;
}

/** Read a file's current content, preferring an open (possibly unsaved)
 * editor buffer over what's on disk. */
function readText(uri: vscode.Uri): string {
  const open = vscode.workspace.textDocuments.find((d) => d.uri.fsPath === uri.fsPath);
  if (open) {
    return open.getText();
  }
  return fs.readFileSync(uri.fsPath, 'utf8');
}

function isCommFile(uri: vscode.Uri): boolean {
  return /\.comm?[a-z0-9]*$/i.test(uri.fsPath);
}

function isExportFile(uri: vscode.Uri): boolean {
  const base = path.basename(uri.fsPath).toLowerCase();
  return base === 'export' || base.endsWith('.export');
}

function listFiles(dir: string, predicate: (name: string) => boolean): string[] {
  try {
    return fs
      .readdirSync(dir)
      .filter(predicate)
      .map((name) => path.join(dir, name));
  } catch {
    return [];
  }
}

/** Pick an .export for a .comm: prefer ones that reference the comm; prompt
 * when the choice is ambiguous. Returns undefined if none exist. */
async function findExportForComm(commPath: string): Promise<vscode.Uri | undefined> {
  const dir = path.dirname(commPath);
  const commName = path.basename(commPath);
  const exports = listFiles(dir, (n) => n === 'export' || n.endsWith('.export'));
  if (exports.length === 0) {
    return undefined;
  }
  const referencing = exports.filter((p) => {
    try {
      return exportReferencesComm(fs.readFileSync(p, 'utf8'), commName);
    } catch {
      return false;
    }
  });
  const candidates = referencing.length > 0 ? referencing : exports;
  if (candidates.length === 1) {
    return vscode.Uri.file(candidates[0]);
  }
  const pick = await vscode.window.showQuickPick(
    candidates.map((p) => ({ label: path.basename(p), description: p })),
    { title: 'Select the .export file for this study' }
  );
  return pick ? vscode.Uri.file(pick.description!) : undefined;
}

/** Find the .comm for an .export: trust its `F comm` declaration, else look
 * for .comm files alongside it. */
async function findCommForExport(exportPath: string): Promise<vscode.Uri | undefined> {
  const dir = path.dirname(exportPath);
  try {
    const declared = commNameFromExport(fs.readFileSync(exportPath, 'utf8'));
    if (declared) {
      const candidate = path.join(dir, declared);
      if (fs.existsSync(candidate)) {
        return vscode.Uri.file(candidate);
      }
    }
  } catch {
    /* fall through to directory scan */
  }
  const comms = listFiles(dir, (n) => /\.comm?[a-z0-9]*$/i.test(n));
  if (comms.length === 0) {
    return undefined;
  }
  if (comms.length === 1) {
    return vscode.Uri.file(comms[0]);
  }
  const pick = await vscode.window.showQuickPick(
    comms.map((p) => ({ label: path.basename(p), description: p })),
    { title: 'Select the command file (.comm) for this study' }
  );
  return pick ? vscode.Uri.file(pick.description!) : undefined;
}

async function resolveStudy(): Promise<ResolvedStudy | undefined> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('Open a .comm or .export file to validate the study.');
    return undefined;
  }
  const uri = editor.document.uri;

  let commUri: vscode.Uri | undefined;
  let exportUri: vscode.Uri | undefined;

  if (editor.document.languageId === 'comm' || isCommFile(uri)) {
    commUri = uri;
    exportUri = await findExportForComm(uri.fsPath);
  } else if (editor.document.languageId === 'export' || isExportFile(uri)) {
    exportUri = uri;
    commUri = await findCommForExport(uri.fsPath);
  } else {
    vscode.window.showErrorMessage('The active file is neither a .comm nor a .export file.');
    return undefined;
  }

  if (!commUri) {
    vscode.window.showErrorMessage('Could not find a command file (.comm) for this study.');
    return undefined;
  }

  return {
    commUri,
    commText: readText(commUri),
    exportUri,
    exportText: exportUri ? readText(exportUri) : undefined,
  };
}

const SEVERITY_MAP: Record<ValidationDiagnostic['severity'], vscode.DiagnosticSeverity> = {
  error: vscode.DiagnosticSeverity.Error,
  warning: vscode.DiagnosticSeverity.Warning,
  information: vscode.DiagnosticSeverity.Information,
};

function publishDiagnostics(
  report: ValidationReport,
  commUri: vscode.Uri,
  exportUri: vscode.Uri | undefined
): void {
  const collection = getDiagnosticCollection();
  collection.clear();
  const byUri = new Map<string, vscode.Diagnostic[]>();
  const target = (file: 'comm' | 'export'): vscode.Uri | undefined =>
    file === 'comm' ? commUri : exportUri;

  for (const d of report.diagnostics) {
    const uri = target(d.file);
    if (!uri) {
      continue;
    }
    const range = new vscode.Range(d.line, d.colStart, d.line, d.colEnd);
    const diag = new vscode.Diagnostic(range, d.message, SEVERITY_MAP[d.severity]);
    diag.source = 'code_aster study';
    diag.code = d.code;
    const key = uri.toString();
    const list = byUri.get(key) ?? [];
    list.push(diag);
    byUri.set(key, list);
  }

  for (const [key, diags] of byUri) {
    collection.set(vscode.Uri.parse(key), diags);
  }
}

function resourceRoot(): string {
  // dist/extension.js → extension root.
  return extensionUri ? extensionUri.fsPath : path.resolve(__dirname, '..');
}

function resourceUri(panel: vscode.WebviewPanel, relativePath: string): string {
  const full = path.join(resourceRoot(), relativePath);
  return panel.webview.asWebviewUri(vscode.Uri.file(full)).toString();
}

/** Rewrite the Vite-built `./assets/...` references to webview URIs and fill
 * in the `${webview.cspSource}` placeholder. Same logic as StudyWebview. */
function preprocessWebviewHtml(panel: vscode.WebviewPanel, html: string, htmlDir: string): string {
  html = html.replace(
    /(<link[^>]+?href="|<script[^>]+?src="|<img[^>]+?src=")([^"]+?)"/g,
    (_m, p1, p2) => {
      const full = path.join(htmlDir, p2);
      return `${p1}${panel.webview.asWebviewUri(vscode.Uri.file(full)).toString()}"`;
    }
  );
  return html.replace(/\$\{webview.cspSource\}/g, panel.webview.cspSource);
}

function buildInitMessage(
  report: ValidationReport,
  study: ResolvedStudy,
  panel: vscode.WebviewPanel
) {
  return {
    command: 'init',
    report,
    commName: path.basename(study.commUri.fsPath),
    exportName: study.exportUri ? path.basename(study.exportUri.fsPath) : '',
    simviaLogoUrl: resourceUri(panel, 'media/images/simvia.svg'),
    simviaLogoDarkUrl: resourceUri(panel, 'media/images/simvia-white.svg'),
    asterLogoUrl: resourceUri(panel, 'media/images/code-aster.svg'),
    asterLogoDarkUrl: resourceUri(panel, 'media/images/code-aster-white.svg'),
  };
}

function showReport(report: ValidationReport, study: ResolvedStudy): void {
  currentStudy = study;
  const root = resourceRoot();

  if (!reportPanel) {
    webviewReady = false;
    reportPanel = vscode.window.createWebviewPanel(
      'vs-code-aster.validationReport',
      'Study validation',
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [vscode.Uri.file(root)],
      }
    );
    const icon = vscode.Uri.file(path.join(root, 'media', 'images', 'icone-validate.svg'));
    reportPanel.iconPath = { light: icon, dark: icon };

    const htmlPath = path.join(root, 'webviews/validation/dist/index.html');
    const html = fs.readFileSync(htmlPath, 'utf8');
    reportPanel.webview.html = preprocessWebviewHtml(reportPanel, html, path.dirname(htmlPath));

    reportPanel.onDidDispose(() => {
      reportPanel = undefined;
      webviewReady = false;
      pendingInit = undefined;
    });
    reportPanel.webview.onDidReceiveMessage((message) => {
      if (message?.command === 'ready') {
        webviewReady = true;
        if (pendingInit) {
          void reportPanel?.webview.postMessage(pendingInit);
          pendingInit = undefined;
        }
        return;
      }
      if (message?.command === 'jump' && typeof message.line === 'number' && currentStudy) {
        const line = Math.max(0, message.line);
        const target =
          message.file === 'export' && currentStudy.exportUri
            ? currentStudy.exportUri
            : currentStudy.commUri;
        void vscode.window.showTextDocument(target, {
          viewColumn: vscode.ViewColumn.One,
          selection: new vscode.Range(line, 0, line, 0),
        });
      }
    });
  }

  reportPanel.title = `Validation: ${path.basename(study.commUri.fsPath)}`;
  const initMsg = buildInitMessage(report, study, reportPanel);
  if (webviewReady) {
    void reportPanel.webview.postMessage(initMsg);
  } else {
    pendingInit = initMsg;
  }
  reportPanel.reveal(vscode.ViewColumn.Beside, true);
}

async function runValidation(): Promise<void> {
  const study = await resolveStudy();
  if (!study) {
    return;
  }

  let client;
  try {
    client = LspServer.instance.client;
  } catch {
    client = undefined;
  }
  if (!client || !client.isRunning?.()) {
    vscode.window.showErrorMessage(
      'The code_aster language server is not running. Cannot validate the study.'
    );
    return;
  }

  let report: ValidationReport;
  try {
    report = (await client.sendRequest('codeaster/validateStudy', {
      commText: study.commText,
      exportText: study.exportText ?? '',
    })) as ValidationReport;
  } catch (err) {
    vscode.window.showErrorMessage(`Study validation failed: ${(err as Error).message}`);
    return;
  }

  if (!report || !Array.isArray(report.commands)) {
    vscode.window.showErrorMessage('Study validation returned an unexpected result.');
    return;
  }

  publishDiagnostics(report, study.commUri, study.exportUri);
  showReport(report, study);
}

export function registerStudyValidation(context: vscode.ExtensionContext): vscode.Disposable {
  extensionUri = context.extensionUri;
  const disposable = vscode.commands.registerCommand('vs-code-aster.validateStudy', () =>
    runValidation()
  );
  context.subscriptions.push(disposable);
  return disposable;
}
