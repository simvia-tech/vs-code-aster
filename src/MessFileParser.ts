import * as vscode from 'vscode';
import * as path from 'path';

interface CMDTAGMatch {
  lineNumber: number; // 0-based
  column?: number;
}

export function parseMessFile(
  content: string,
  exportUri: vscode.Uri,
  commUri: vscode.Uri | undefined
): Map<string, vscode.Diagnostic[]> {
  const diagnostics = new Map<string, vscode.Diagnostic[]>();

  const cmdtagRegex = /^\.\..*__(?:run|stg)\d+_(?:cmd|txt)(\d+)(?::(\d+))?/;
  const tagRegex = /^<([AEF])>/;

  const lines = content.split('\n');
  let lastCMDTAG: CMDTAGMatch | undefined;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) {
      continue;
    }

    const cmdtagMatch = line.match(cmdtagRegex);
    if (cmdtagMatch) {
      // Extract line number (1-based in the file, convert to 0-based)
      const lineNum = parseInt(cmdtagMatch[1], 10) - 1;
      const column = cmdtagMatch[2] ? parseInt(cmdtagMatch[2], 10) - 1 : 0;
      lastCMDTAG = { lineNumber: lineNum, column };
      continue;
    }

    const tagMatch = line.match(tagRegex);
    if (tagMatch) {
      const severity = tagMatch[1];
      const isSeverity =
        severity === 'A' ? vscode.DiagnosticSeverity.Warning : vscode.DiagnosticSeverity.Error;

      // Collect the message (the tag line itself + subsequent text lines)
      const messageLines: string[] = [line];
      for (let j = i + 1; j < lines.length; j++) {
        const nextLine = lines[j];
        if (!nextLine.trim()) {
          break;
        }
        if (nextLine.match(tagRegex) || nextLine.match(cmdtagRegex)) {
          break;
        }
        messageLines.push(nextLine);
        i = j;
      }

      const message = messageLines.join('\n').trim();

      // Determine target URI and position
      let targetUri: vscode.Uri;
      let range: vscode.Range;

      if (lastCMDTAG && commUri) {
        // Attach to .comm file at the CMDTAG line
        targetUri = commUri;
        range = new vscode.Range(
          new vscode.Position(lastCMDTAG.lineNumber, lastCMDTAG.column || 0),
          new vscode.Position(lastCMDTAG.lineNumber, lastCMDTAG.column || 0)
        );
      } else {
        // Attach to .export file at start
        targetUri = exportUri;
        range = new vscode.Range(new vscode.Position(0, 0), new vscode.Position(0, 0));
      }

      const diagnostic = new vscode.Diagnostic(range, message, isSeverity);
      diagnostic.source = 'code-aster';

      const uriKey = targetUri.toString();
      if (!diagnostics.has(uriKey)) {
        diagnostics.set(uriKey, []);
      }
      diagnostics.get(uriKey)!.push(diagnostic);

      lastCMDTAG = undefined;
    }
  }

  return diagnostics;
}
