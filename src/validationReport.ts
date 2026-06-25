/**
 * Shared types and pure helpers for the study validation report.
 *
 * No `vscode` import and no DOM rendering, so this is consumed by both the
 * extension host (`StudyValidation.ts`, for diagnostics) and the Svelte
 * report webview (`webviews/validation`, for display). The shapes mirror what
 * the Python `validate_study` request returns (see
 * `python/lsp/validation_manager.py`).
 */

export type CheckResult = boolean | null;

export interface CommandRow {
  concept: string;
  command: string;
  line: number; // 0-based line of the command in the .comm
  syntactic: CheckResult;
  dependency: CheckResult;
  naming: CheckResult;
  used: CheckResult;
}

export interface IoRow {
  unit: number;
  direction: string; // "Input" | "Output" | "Unknown"
  file: string;
  exportType: string;
  usedIn: string;
  status: 'ok' | 'warning' | 'error';
}

export interface ValidationDiagnostic {
  file: 'comm' | 'export';
  line: number;
  colStart: number;
  colEnd: number;
  severity: 'error' | 'warning' | 'information';
  code: string;
  message: string;
}

export interface ValidationReport {
  commands: CommandRow[];
  io: IoRow[];
  diagnostics: ValidationDiagnostic[];
  hasExport: boolean;
}

const OK = '✅';
const ERR = '❌';
const WARN = '⚠️';
const INFO = 'ℹ️';
const NA = '—';

/** Glyph for a command-table check. `false` renders as an error for the
 * structural checks (syntactic/dependency) and a warning for the advisory
 * ones (naming/used), matching the diagnostic severities. */
export function checkGlyph(value: CheckResult, advisory = false): string {
  if (value === null) {
    return NA;
  }
  if (value) {
    return OK;
  }
  return advisory ? WARN : ERR;
}

export function ioGlyph(status: IoRow['status']): string {
  if (status === 'ok') {
    return OK;
  }
  return status === 'warning' ? WARN : ERR;
}

export function severityGlyph(severity: ValidationDiagnostic['severity']): string {
  if (severity === 'error') {
    return ERR;
  }
  return severity === 'warning' ? WARN : INFO;
}

/** What each glyph means, shown as a legend in the report — one entry per
 * line so each symbol gets a clear, readable explanation. */
export const GLYPH_LEGEND: ReadonlyArray<{ glyph: string; text: string }> = [
  { glyph: OK, text: 'passed' },
  { glyph: WARN, text: "warning — worth checking, won't necessarily fail the run" },
  { glyph: ERR, text: 'problem — likely to break the run' },
  { glyph: NA, text: 'not applicable' },
];

/** One-line explanation of each command-table column, used for the column
 * header tooltips so the glyphs aren't cryptic. */
export const CHECK_DOCS: Record<'syntactic' | 'dependency' | 'naming' | 'used', string> = {
  syntactic:
    'Command is recognised by the catalog and well-formed (balanced parentheses, known keywords).',
  dependency: 'Concepts referenced by this command are defined earlier in the study.',
  naming: 'Concept name is valid, is not a redefinition, and a produced result is assigned a name.',
  used: 'The concept produced by this command is referenced later in the study.',
};

export interface ReportCounts {
  errors: number;
  warnings: number;
}

export function countDiagnostics(report: ValidationReport): ReportCounts {
  let errors = 0;
  let warnings = 0;
  for (const d of report.diagnostics) {
    if (d.severity === 'error') {
      errors++;
    } else if (d.severity === 'warning') {
      warnings++;
    }
  }
  return { errors, warnings };
}
