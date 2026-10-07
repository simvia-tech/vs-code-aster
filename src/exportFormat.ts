// Pure .export formatting logic, free of any `vscode` import so it can be
// shared by the extension host, the export DocumentFormattingEditProvider
// (src/ExportFormatter.ts), and the Svelte webviews' Vite bundles.

interface Entry {
  comments: string[];
  line: string;
  type: string;
  head?: 'F' | 'R';
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
  if (a.head !== b.head) {
    return a.head === 'F' ? -1 : 1;
  }
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
  unknown: '# Unknown lines',
} as const;

const VALID_IO_FLAGS = new Set(['D', 'DC', 'R', 'RC']);

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

export function isAutoMetaComment(trimmed: string): boolean {
  return AUTO_META_COMMENTS.has(trimmed) || FILENAME_HEADER_RE.test(trimmed);
}

/**
 * Pure formatter: takes raw .export content, returns formatted content.
 * Used by both the DocumentFormattingEditProvider and the save path so they
 * produce identical output. With `autoComments` false, the header and section
 * comments are left out (and stripped from files that already have them).
 */
export function formatExportContent(text: string, filename?: string, autoComments = true): string {
  const lines = text.split(/\r?\n/);
  const pEntries: Entry[] = [];
  const fEntries: Entry[] = [];
  const unknownEntries: Entry[] = [];
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
    const isValidFR =
      (head === 'F' || head === 'R') && tokens.length === 5 && VALID_IO_FLAGS.has(tokens[3] ?? '');
    if (head === 'P' && tokens.length >= 2) {
      pEntries.push({ comments: pendingComments, line: trimmed, type: '' });
      pendingComments = [];
    } else if (isValidFR) {
      const direction: 'D' | 'R' = tokens[3] === 'D' || tokens[3] === 'DC' ? 'D' : 'R';
      fEntries.push({
        comments: pendingComments,
        line: trimmed,
        type: tokens[1] ?? '',
        head: head as 'F' | 'R',
        direction,
      });
      pendingComments = [];
    } else {
      unknownEntries.push({ comments: pendingComments, line: trimmed, type: '' });
      pendingComments = [];
    }
  }

  const dEntries = fEntries.filter((e) => e.direction === 'D').sort(byType);
  const rEntries = fEntries.filter((e) => e.direction === 'R').sort(byType);

  const renderSection = (entries: Entry[]): string =>
    entries.map((e) => [...e.comments, e.line].join('\n')).join('\n');

  const sections: string[] = [];
  if (autoComments) {
    const headerLines: string[] = [];
    if (filename) {
      headerLines.push(`# ${filename}`);
    }
    headerLines.push(...STATIC_HEADER_LINES);
    sections.push(headerLines.join('\n'));
  }
  const pushSection = (header: string, entries: Entry[]) => {
    if (entries.length > 0) {
      const body = renderSection(entries);
      sections.push(autoComments ? `${header}\n${body}` : body);
    }
  };
  pushSection(SECTION_HEADERS.parameters, pEntries);
  pushSection(SECTION_HEADERS.inputs, dEntries);
  pushSection(SECTION_HEADERS.outputs, rEntries);
  pushSection(SECTION_HEADERS.unknown, unknownEntries);
  if (pendingComments.length > 0) {
    sections.push(pendingComments.join('\n'));
  }

  return sections.join('\n\n') + '\n';
}
