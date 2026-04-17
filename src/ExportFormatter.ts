import * as vscode from 'vscode';

interface Entry {
  comments: string[];
  line: string;
  type: string;
  direction?: 'D' | 'R';
}

const TYPE_PRIORITY: Record<string, number> = {
  comm: 1,
  med: 2,
  mmed: 2,
  rmed: 3,
  mess: 5,
};

function typeRank(type: string): number {
  return TYPE_PRIORITY[type] ?? 4;
}

function byType(a: Entry, b: Entry): number {
  const pa = typeRank(a.type);
  const pb = typeRank(b.type);
  if (pa !== pb) {
    return pa - pb;
  }
  return a.type.localeCompare(b.type);
}

export class ExportFormatter implements vscode.DocumentFormattingEditProvider {
  public provideDocumentFormattingEdits(document: vscode.TextDocument): vscode.TextEdit[] {
    const lines = document.getText().split(/\r?\n/);
    const pEntries: Entry[] = [];
    const fEntries: Entry[] = [];
    let pendingComments: string[] = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed === '') {
        continue;
      }
      if (trimmed.startsWith('#')) {
        pendingComments.push(trimmed);
        continue;
      }
      const tokens = trimmed.split(/\s+/);
      const head = tokens[0];
      if (head === 'P') {
        pEntries.push({ comments: pendingComments, line: trimmed, type: '' });
        pendingComments = [];
      } else if (head === 'F') {
        const direction: 'D' | 'R' = tokens[3] === 'D' ? 'D' : 'R';
        fEntries.push({
          comments: pendingComments,
          line: trimmed,
          type: tokens[1] ?? '',
          direction,
        });
        pendingComments = [];
      }
    }

    const dEntries = fEntries.filter((e) => e.direction === 'D').sort(byType);
    const rEntries = fEntries.filter((e) => e.direction === 'R').sort(byType);

    const renderSection = (entries: Entry[]): string =>
      entries.map((e) => [...e.comments, e.line].join('\n')).join('\n');

    const sections: string[] = [];
    if (pEntries.length > 0) {
      sections.push(renderSection(pEntries));
    }
    if (dEntries.length > 0) {
      sections.push(renderSection(dEntries));
    }
    if (rEntries.length > 0) {
      sections.push(renderSection(rEntries));
    }
    if (pendingComments.length > 0) {
      sections.push(pendingComments.join('\n'));
    }

    const formatted = sections.join('\n\n') + '\n';

    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );

    return [vscode.TextEdit.replace(fullRange, formatted)];
  }
}
