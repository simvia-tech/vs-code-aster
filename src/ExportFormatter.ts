import * as vscode from 'vscode';

interface Entry {
  comments: string[];
  line: string;
  type: string;
  direction?: 'D' | 'R';
}

// Ordering priority for F-line types within their D/R section.
// Matches the webview's ALLOWED_TYPES order.
const TYPE_ORDER = [
  'comm',
  'mmed',
  'rmed',
  'mess',
  'nom',
  'base',
  'mail',
  'libr',
  'tab',
  'msh',
  'dat',
];

function typeRank(type: string): number {
  const i = TYPE_ORDER.indexOf(type);
  return i >= 0 ? i : TYPE_ORDER.length;
}

function byType(a: Entry, b: Entry): number {
  const pa = typeRank(a.type);
  const pb = typeRank(b.type);
  if (pa !== pb) {
    return pa - pb;
  }
  return a.type.localeCompare(b.type);
}

const SECTION_HEADERS = {
  parameters: '# Simulation parameters',
  inputs: '# Input files',
  outputs: '# Output files',
} as const;

const STATIC_HEADER_LINES = [
  '# This file was generated using VS Code Aster - https://github.com/simvia-tech/vs-code-aster',
  '# VS Code Aster is an open-source project maintained by Simvia - https://simvia.tech',
] as const;

// Our own auto-emitted meta comments. When re-saving a formatted file we drop
// them during parsing and re-emit fresh copies, so they never stack.
const AUTO_META_COMMENTS = new Set<string>([
  ...STATIC_HEADER_LINES,
  ...Object.values(SECTION_HEADERS),
]);

// A comment like "# something.export" is also an auto header (the filename
// line) — the exact string varies per file so we match the shape instead.
const FILENAME_HEADER_RE = /^#\s*\S+\.export\s*$/i;

function isAutoMetaComment(trimmed: string): boolean {
  return AUTO_META_COMMENTS.has(trimmed) || FILENAME_HEADER_RE.test(trimmed);
}

/**
 * Pure formatter: takes raw .export content, returns formatted content.
 * Used by both the DocumentFormattingEditProvider and the save path so they
 * produce identical output.
 */
export function formatExportContent(text: string, filename?: string): string {
  const lines = text.split(/\r?\n/);
  const pEntries: Entry[] = [];
  const fEntries: Entry[] = [];
  let pendingComments: string[] = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed === '') {
      continue;
    }
    if (trimmed.startsWith('#')) {
      if (!isAutoMetaComment(trimmed)) {
        pendingComments.push(trimmed);
      }
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

  const headerLines: string[] = [];
  if (filename) {
    headerLines.push(`# ${filename}`);
  }
  headerLines.push(...STATIC_HEADER_LINES);
  const sections: string[] = [headerLines.join('\n')];
  if (pEntries.length > 0) {
    sections.push(`${SECTION_HEADERS.parameters}\n${renderSection(pEntries)}`);
  }
  if (dEntries.length > 0) {
    sections.push(`${SECTION_HEADERS.inputs}\n${renderSection(dEntries)}`);
  }
  if (rEntries.length > 0) {
    sections.push(`${SECTION_HEADERS.outputs}\n${renderSection(rEntries)}`);
  }
  if (pendingComments.length > 0) {
    sections.push(pendingComments.join('\n'));
  }

  return sections.join('\n\n') + '\n';
}

export class ExportFormatter implements vscode.DocumentFormattingEditProvider {
  public provideDocumentFormattingEdits(document: vscode.TextDocument): vscode.TextEdit[] {
    const filename = document.uri.path.split('/').pop() ?? undefined;
    const formatted = formatExportContent(document.getText(), filename);
    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );
    return [vscode.TextEdit.replace(fullRange, formatted)];
  }
}
