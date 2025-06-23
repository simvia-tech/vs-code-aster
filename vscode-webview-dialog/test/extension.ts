
import * as vscode from 'vscode';
import * as path from 'path';
import * as dialog from 'vscode-webview-dialog';

export async function activate(context: vscode.ExtensionContext): Promise<void> {
	vscode.commands.registerCommand('vscode-webview-dialog-test.showDialog', showWebview);
}

export async function deactivate(): Promise<void> {
}

interface TestDialogResult {
	name: string;
}

async function showWebview(): Promise<void> {
	const testDir = path.resolve(__dirname, '..');
	const d = new dialog.WebviewDialog<TestDialogResult>(
		'webview-dialog-test', testDir, 'dialog.html');
	const result: TestDialogResult | null = await d.getResult();

	if (result) {
		vscode.window.showInformationMessage(
			"Le fichier a été créé, il est rangé : " + JSON.stringify(result));
	} else {
		vscode.window.showInformationMessage(
			"Aucun fichier n'a été créé.");
	}
}
