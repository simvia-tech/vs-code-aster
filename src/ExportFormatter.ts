import * as vscode from 'vscode';
import { formatExportContent } from './exportFormat';

// Re-export so existing importers (ExportEditor, scenario generators) keep
// working through this module; the pure logic now lives in ./exportFormat.
export { formatExportContent };

/** Whether to emit the auto header and section comments in .export files. */
export function exportAutoComments(): boolean {
  return vscode.workspace
    .getConfiguration('vs-code-aster')
    .get<boolean>('exportAutoComments', true);
}

export class ExportFormatter implements vscode.DocumentFormattingEditProvider {
  public provideDocumentFormattingEdits(document: vscode.TextDocument): vscode.TextEdit[] {
    const filename = document.uri.path.split('/').pop() ?? undefined;
    const formatted = formatExportContent(document.getText(), filename, exportAutoComments());
    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );
    return [vscode.TextEdit.replace(fullRange, formatted)];
  }
}
