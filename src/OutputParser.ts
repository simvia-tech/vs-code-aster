import * as vscode from 'vscode';

interface CMDTAGMatch {
  lineNumber: number; // 0-based
  column?: number;
}

/**
 * Parses captured code_aster run output (stdout+stderr) and produces diagnostics.
 *
 * Handles:
 *   - Code_aster box-drawn `<A>` (warning) / `<E>` / `<F>` (error) messages with CMDTAG mapping
 *   - Python tracebacks (NameError, AttributeError, RuntimeError, ...)
 *   - Python SyntaxError blocks (caret-style, no traceback header)
 *   - Fatal Python errors (e.g. Segmentation fault)
 *   - MED / Fortran-layer errors (`filename.c [N] : Erreur ...`)
 */
export function parseRunOutput(
  content: string,
  exportUri: vscode.Uri,
  commFiles: Map<string, vscode.Uri>
): Map<string, vscode.Diagnostic[]> {
  const diagnostics = new Map<string, vscode.Diagnostic[]>();

  const addDiagnostic = (uri: vscode.Uri, diag: vscode.Diagnostic) => {
    const key = uri.toString();
    if (!diagnostics.has(key)) {
      diagnostics.set(key, []);
    }
    diagnostics.get(key)!.push(diag);
  };

  const resolveSourceFile = (filePath: string): { uri: vscode.Uri; matched: boolean } => {
    const match = filePath.match(/([^/\\]+?)(?:\.changed\.py)?$/);
    if (match && commFiles.has(match[1])) {
      return { uri: commFiles.get(match[1])!, matched: true };
    }
    return { uri: exportUri, matched: false };
  };

  const makeRange = (line: number, col = 0): vscode.Range =>
    new vscode.Range(new vscode.Position(line, col), new vscode.Position(line, col));

  const lines = content.split('\n');

  const cmdtagRegex = /^\.\. _(?:run|stg)\d+_(?:cmd|txt)(\d+)(?::(\d+))?/;
  // Match `<A>`, `<E>`, `<F>` followed by whitespace or `<` (next tag) — not `_`
  // which appears in cave's status flags like `<A>_ALARM`, `<F>_ABNORMAL_ABORT`.
  const tagRegex = /<([AEF])>(?!_)/;
  const exceptionRegex = /^([A-Z][A-Za-z_]*(?:Error|Exception|Warning|Interrupt|Exit)):\s*(.*)/;
  const fileRefRegex = /File "([^"]+)", line (\d+)/;
  const medErrorRegex = /^(\w+\.c)\s*\[\d+\]\s*:\s*(.*)/i;
  const currentFileRegex = /^__file__\s*=\s*r?["']([^"']+)["']/;

  let lastCMDTAG: CMDTAGMatch | undefined;
  let currentCommUri: vscode.Uri | undefined;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) {
      continue;
    }

    // Track the current active command file via `__file__ = r"..."` markers
    // emitted by cave in each processed command file's preamble.
    const currentFileMatch = line.match(currentFileRegex);
    if (currentFileMatch) {
      const basename = currentFileMatch[1].split(/[/\\]/).pop() || '';
      if (commFiles.has(basename)) {
        currentCommUri = commFiles.get(basename);
      }
      continue;
    }

    // CMDTAG marker: remember for the next code_aster box message
    const cmdtagMatch = line.match(cmdtagRegex);
    if (cmdtagMatch) {
      const lineNum = parseInt(cmdtagMatch[1], 10) - 1;
      const column = cmdtagMatch[2] ? parseInt(cmdtagMatch[2], 10) - 1 : 0;
      lastCMDTAG = { lineNumber: lineNum, column };
      continue;
    }

    // 1. Code_aster box message: `<A>` / `<E>` / `<F>`
    const tagMatch = line.match(tagRegex);
    if (tagMatch) {
      const severity = tagMatch[1];
      const diagSeverity =
        severity === 'A' ? vscode.DiagnosticSeverity.Warning : vscode.DiagnosticSeverity.Error;

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

      const message = messageLines
        .filter((l) => l.trim() && !/^[\s║╔╚═╗╝]+$/.test(l))
        .map((l) => l.replace(/[║╔╚╗╝]/g, '').trim())
        .filter((l) => l)
        .join('\n')
        .trim();

      let targetUri: vscode.Uri;
      let range: vscode.Range;
      if (lastCMDTAG && currentCommUri) {
        targetUri = currentCommUri;
        range = makeRange(lastCMDTAG.lineNumber, lastCMDTAG.column || 0);
      } else {
        targetUri = exportUri;
        range = makeRange(0);
      }

      const diag = new vscode.Diagnostic(range, message, diagSeverity);
      diag.source = 'code-aster';
      addDiagnostic(targetUri, diag);
      lastCMDTAG = undefined;
      continue;
    }

    // 2. Python traceback: starts with `Traceback (most recent call last):`
    if (line.trim() === 'Traceback (most recent call last):') {
      const block: string[] = [];
      let lastUserFileRef: { path: string; lineNumber: number } | undefined;
      let exceptionLine = '';
      let j = i + 1;
      for (; j < lines.length; j++) {
        const cur = lines[j];
        if (!cur.trim()) {
          continue;
        }
        const fileMatch = cur.match(fileRefRegex);
        if (fileMatch) {
          const filePath = fileMatch[1];
          const resolved = resolveSourceFile(filePath);
          if (resolved.matched) {
            lastUserFileRef = { path: filePath, lineNumber: parseInt(fileMatch[2], 10) - 1 };
          } else if (!lastUserFileRef) {
            lastUserFileRef = { path: filePath, lineNumber: parseInt(fileMatch[2], 10) - 1 };
          }
          block.push(cur);
          continue;
        }
        if (cur.startsWith('    ')) {
          block.push(cur);
          continue;
        }
        const excMatch = cur.match(exceptionRegex);
        if (excMatch) {
          exceptionLine = cur.trim();
          break;
        }
        break;
      }
      i = j;

      if (exceptionLine) {
        const targetUri = lastUserFileRef ? resolveSourceFile(lastUserFileRef.path).uri : exportUri;
        const lineNum = lastUserFileRef ? lastUserFileRef.lineNumber : 0;
        const message = [exceptionLine, ...block.slice(-4)].join('\n');
        const diag = new vscode.Diagnostic(
          makeRange(lineNum),
          message,
          vscode.DiagnosticSeverity.Error
        );
        diag.source = 'code-aster';
        addDiagnostic(targetUri, diag);
      }
      continue;
    }

    // 3. Python SyntaxError (no Traceback header). Pattern:
    //   File "...", line N
    //       <code>
    //          ^
    //   SyntaxError: ...
    const fileOnlyMatch = line.match(/^\s*File "([^"]+)", line (\d+)\s*$/);
    if (fileOnlyMatch) {
      const lookahead = lines.slice(i + 1, i + 6);
      const hasCaret = lookahead.some((l) => /^\s*\^+\s*$/.test(l));
      const syntaxIdx = lookahead.findIndex((l) => /^SyntaxError:/.test(l.trim()));
      if (hasCaret && syntaxIdx >= 0) {
        const filePath = fileOnlyMatch[1];
        const lineNum = parseInt(fileOnlyMatch[2], 10) - 1;
        const resolved = resolveSourceFile(filePath);
        const message = [lookahead[syntaxIdx].trim(), ...lookahead.slice(0, syntaxIdx)]
          .map((l) => l.replace(/\s+$/, ''))
          .filter((l) => l)
          .join('\n');
        const diag = new vscode.Diagnostic(
          makeRange(lineNum),
          message,
          vscode.DiagnosticSeverity.Error
        );
        diag.source = 'code-aster';
        addDiagnostic(resolved.uri, diag);
        i += syntaxIdx + 1;
        continue;
      }
    }

    // 4. Fatal Python error. The block is header + `Current thread ...:` +
    // indented `File "..."` lines, ending at `Extension modules:` or a
    // terminal status line. Scan the next ~40 lines for the deepest user
    // source file reference.
    if (line.startsWith('Fatal Python error:')) {
      const header = line.trim();
      let userFileRef: { path: string; lineNumber: number } | undefined;
      let j = i + 1;
      const end = Math.min(lines.length, i + 40);
      for (; j < end; j++) {
        const cur = lines[j];
        if (/^Extension modules:/.test(cur) || /^Segmentation fault/.test(cur.trim())) {
          break;
        }
        const fileMatch = cur.match(fileRefRegex);
        if (fileMatch) {
          const resolved = resolveSourceFile(fileMatch[1]);
          if (resolved.matched) {
            userFileRef = { path: fileMatch[1], lineNumber: parseInt(fileMatch[2], 10) - 1 };
          } else if (!userFileRef) {
            userFileRef = { path: fileMatch[1], lineNumber: parseInt(fileMatch[2], 10) - 1 };
          }
        }
      }
      i = j;

      const targetUri = userFileRef ? resolveSourceFile(userFileRef.path).uri : exportUri;
      const lineNum = userFileRef ? userFileRef.lineNumber : 0;
      const diag = new vscode.Diagnostic(
        makeRange(lineNum),
        header,
        vscode.DiagnosticSeverity.Error
      );
      diag.source = 'code-aster';
      addDiagnostic(targetUri, diag);
      continue;
    }

    // 5. MED / Fortran-layer error: `filename.c [N] : Erreur ...`
    const medMatch = line.match(medErrorRegex);
    if (medMatch && /erreur|error/i.test(line)) {
      const messageLines = [line.trim()];
      let j = i + 1;
      for (; j < lines.length && j < i + 5; j++) {
        const cur = lines[j];
        if (cur.match(medErrorRegex)) {
          messageLines.push(cur.trim());
          continue;
        }
        break;
      }
      i = j - 1;

      const diag = new vscode.Diagnostic(
        makeRange(0),
        messageLines.join('\n'),
        vscode.DiagnosticSeverity.Error
      );
      diag.source = 'code-aster';
      addDiagnostic(exportUri, diag);
      continue;
    }
  }

  // Deduplicate: Python tracebacks are sometimes printed twice by the runtime
  // (once to stderr, once tee'd to fort.6). Collapse identical diagnostics
  // keyed by (line, first message line).
  for (const [key, list] of diagnostics) {
    const seen = new Set<string>();
    const unique: vscode.Diagnostic[] = [];
    for (const d of list) {
      const firstLine = d.message.split('\n')[0];
      const sig = `${d.range.start.line}:${d.severity}:${firstLine}`;
      if (!seen.has(sig)) {
        seen.add(sig);
        unique.push(d);
      }
    }
    diagnostics.set(key, unique);
  }

  return diagnostics;
}
