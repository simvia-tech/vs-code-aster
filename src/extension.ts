/**
 * Main entry point for the Code-Aster VS Code extension.
 * Handles activation, command registration, and integration with the mesh viewer and export dialog.
 */
import * as vscode from 'vscode';
import * as path from 'path';

import { VisuManager } from './VisuManager';
import { ExportEditor } from './ExportEditor';
import { ExportFormatter } from './ExportFormatter';
import { RunAster } from './RunAster';
import { LspServer } from './LspServer';
import { StatusBar } from './StatusBar';
import { activateMedLanguageSync } from './MedLanguageSync';
import { MedEditorProvider, STATIC_MED_EXTS } from './MedEditorProvider';
import { activateMedAutoDetect, isExtensionConfigured, openAsMedMesh } from './MedAutoDetect';
import { setTelemetryContext } from './telemetry';

/**
 * Main activation function for the extension. Registers all commands.
 *
 * @param context The VS Code extension context.
 */
export async function activate(context: vscode.ExtensionContext) {
  // Set up telemetry context
  setTelemetryContext(context);

  // Set up diagnostics collection for code-aster output parsing
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('code-aster');
  RunAster.init(diagnosticCollection);
  context.subscriptions.push(diagnosticCollection);

  const runaster = vscode.commands.registerCommand('vs-code-aster.run-aster', () => {
    RunAster.runCodeAster();
  });

  const createExportDoc = vscode.commands.registerCommand('vs-code-aster.exportDoc', () => {
    ExportEditor.initExportEditor();
  });

  context.subscriptions.push(
    vscode.languages.registerDocumentFormattingEditProvider(
      { language: 'export' },
      new ExportFormatter()
    )
  );

  const createMesh = vscode.commands.registerCommand('vs-code-aster.meshViewer', () => {
    VisuManager.instance.createOrShowMeshViewer();
  });

  await LspServer.instance.start(context);
  const lspServer = vscode.commands.registerCommand('vs-code-aster.restartLSPServer', async () => {
    LspServer.instance.restart();
  });

  StatusBar.instance.activate(context);

  activateMedLanguageSync(context);

  // Register the custom editor for .med/.mmed/.rmed files so they open
  // directly in the mesh viewer instead of the binary text editor.
  context.subscriptions.push(MedEditorProvider.register(context));

  // Auto-detect MED files by HDF5 magic bytes, and offer to add their
  // extension to the list — avoids having to edit settings manually.
  activateMedAutoDetect(context);

  const addToMedExtensions = vscode.commands.registerCommand(
    'vs-code-aster.addToMedExtensions',
    async (resource?: vscode.Uri) => {
      const uri =
        resource instanceof vscode.Uri ? resource : vscode.window.activeTextEditor?.document.uri;
      if (!uri) {
        vscode.window.showWarningMessage('No file to open as MED mesh.');
        return;
      }
      await openAsMedMesh(uri);
    }
  );
  context.subscriptions.push(addToMedExtensions);

  // For user-configured numeric MED extensions (e.g. .71, .72), VS Code
  // opens them as text (our customEditors selectors are static). We listen
  // for new tabs and, if a tab points at a file whose extension is in the
  // configured MED list, close the text tab and open with the mesh viewer.
  // We match against `medFileExtensions` directly (rather than
  // `languageId === 'med'`) because `files.associations` updates are applied
  // lazily by VS Code — relying on language ID would require a window reload.
  const redirectTextTabToViewer = async (tab: vscode.Tab): Promise<void> => {
    if (!(tab.input instanceof vscode.TabInputText)) {
      return;
    }
    const uri = tab.input.uri;
    if (uri.scheme !== 'file') {
      return;
    }
    const ext = path.extname(uri.fsPath).toLowerCase();
    if (STATIC_MED_EXTS.has(ext)) {
      return;
    }
    if (!isExtensionConfigured(ext)) {
      return;
    }

    // Close the text tab first so we don't end up with two tabs for the
    // same file (text + custom editor).
    await vscode.window.tabGroups.close(tab);
    await vscode.commands.executeCommand('vscode.openWith', uri, MedEditorProvider.viewType);
  };

  context.subscriptions.push(
    vscode.window.tabGroups.onDidChangeTabs((event) => {
      for (const tab of event.opened) {
        void redirectTextTabToViewer(tab);
      }
    })
  );

  // Handle the case where VS Code restored a text tab at startup for a file
  // whose extension was added to the MED list in a previous session.
  const activeTab = vscode.window.tabGroups.activeTabGroup?.activeTab;
  if (activeTab) {
    void redirectTextTabToViewer(activeTab);
  }

  context.subscriptions.push(runaster);
  context.subscriptions.push(createExportDoc);
  context.subscriptions.push(createMesh);
  context.subscriptions.push(lspServer);
}

export function deactivate(): Thenable<void> | undefined {
  return LspServer.instance.deactivate();
}
