/**
 * Pure helpers for associating a `.comm` with its `.export` (and vice
 * versa). No `vscode` import so they can be unit-tested directly; the
 * filesystem/UI glue lives in `StudyValidation.ts`.
 */

import * as path from 'path';

/**
 * Extract the command-file path declared in an `.export` file, i.e. the
 * `name` token of the `F comm <name> ...` line. Returns the path as written
 * (may be relative or absolute), or undefined when there is no comm declaration.
 */
export function commNameFromExport(exportText: string): string | undefined {
  for (const raw of exportText.split(/\r?\n/)) {
    const clean = raw.split('#')[0].trim();
    if (!clean) {
      continue;
    }
    const tokens = clean.split(/\s+/);
    if ((tokens[0] === 'F' || tokens[0] === 'R') && tokens.length === 5 && tokens[1] === 'comm') {
      return tokens[2];
    }
  }
  return undefined;
}

/**
 * Whether an `.export` file plausibly belongs to a given `.comm`. Matches if
 * its declared comm file shares the basename, or — as a looser fallback that
 * mirrors the mesh-viewer association logic — if the comm filename appears
 * anywhere in the export text.
 */
export function exportReferencesComm(exportText: string, commFileName: string): boolean {
  const declared = commNameFromExport(exportText);
  if (declared && path.basename(declared) === commFileName) {
    return true;
  }
  return exportText.includes(commFileName);
}
