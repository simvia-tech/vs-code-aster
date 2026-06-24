/**
 * Logical unit assignment for generated studies. These values mirror the
 * canonical defaults in `webviews/export/src/lib/types.ts` (DEFAULT_UNITS) —
 * comm=1, mmed=20, rmed=80, mess=6 — and are the single source of truth shared
 * by the .comm generator (UNITE=...) and the .export generator (F/R lines) so
 * the two files always agree.
 */
export const STUDY_UNITS = {
  comm: 1,
  mesh: 20, // mmed input
  result: 80, // rmed output
  message: 6, // mess output
} as const;

/**
 * Verifies that every `UNITE=N` referenced in the .comm has a matching F/R line
 * with unit N in the .export, and that the .export assigns no unit twice
 * (unit 0 excepted — `nom`-style files legitimately share it). Returns the list
 * of problems found (empty array = consistent). Used by the golden tests.
 */
export function checkUnitsConsistent(comm: string, exportText: string): string[] {
  const problems: string[] = [];

  const commUnits = new Set<number>();
  for (const m of comm.matchAll(/UNITE\s*=\s*(\d+)/g)) {
    commUnits.add(Number(m[1]));
  }

  const exportUnits = new Map<number, number>(); // unit -> count
  for (const m of exportText.matchAll(/^[FR]\s+\S+\s+\S+\s+\S+\s+(\d+)\s*$/gm)) {
    const u = Number(m[1]);
    exportUnits.set(u, (exportUnits.get(u) ?? 0) + 1);
  }

  for (const u of commUnits) {
    if (!exportUnits.has(u)) {
      problems.push(`.comm references UNITE=${u} but no .export file uses unit ${u}`);
    }
  }

  for (const [u, count] of exportUnits) {
    if (u !== 0 && count > 1) {
      problems.push(`.export assigns unit ${u} to ${count} files (collision)`);
    }
  }

  return problems;
}
