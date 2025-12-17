/**
 * Main entry point for the Code-Aster VS Code extension.
 * Handles activation, command registration, and integration with the mesh viewer and export dialog.
 */
import * as vscode from 'vscode';

import { VisuManager } from './VisuManager';
import { ExportEditor } from './ExportEditor';
import { RunAster } from './RunAster';
import { LspServer } from './LspServer';
import { StatusBar } from './StatusBar';
import { setTelemetryContext } from './telemetry';


/**
 * Main activation function for the extension. Registers all commands.
 *
 * @param context The VS Code extension context.
 */
export async function activate(context: vscode.ExtensionContext) {
    
    // Set up telemetry context
    setTelemetryContext(context);

    const runaster = vscode.commands.registerCommand('vs-code-aster.run-aster', () => {
        RunAster.runCodeAster();
	});

	const createExportDoc = vscode.commands.registerCommand('vs-code-aster.exportDoc', () => {
        ExportEditor.initExportEditor();
	});

    const createMesh = vscode.commands.registerCommand('vs-code-aster.meshViewer', () => {
        VisuManager.instance.createOrShowMeshViewer();
	});

    await LspServer.instance.start(context);
    const lspServer = vscode.commands.registerCommand('vs-code-aster.restartLSPServer', async () => {
        LspServer.instance.restart();
    });
    
    StatusBar.instance.activate(context);

	context.subscriptions.push(runaster);
	context.subscriptions.push(createExportDoc);
    context.subscriptions.push(createMesh);
    context.subscriptions.push(lspServer);
}

export function deactivate(): Thenable<void> | undefined {
    return LspServer.instance.deactivate();
}