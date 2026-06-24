import { StudySpec } from './spec';
import { STUDY_UNITS } from './units';
import { formatExportContent } from '../exportFormat';

/**
 * Generates the .export file matching `generateComm(spec)`. The logical units
 * come from the shared STUDY_UNITS table, so the comm (UNITE=...) and the export
 * (F/R lines) always agree. Formatting is delegated to the same
 * `formatExportContent` used by the export editor, so generated and
 * hand-edited files look identical.
 */
export function generateExport(spec: StudySpec): string {
  const raw = [
    `F comm ${spec.baseName}.comm D ${STUDY_UNITS.comm}`,
    `F mmed ${spec.meshFileName} D ${STUDY_UNITS.mesh}`,
    `F mess ${spec.baseName}.mess R ${STUDY_UNITS.message}`,
    `F rmed ${spec.baseName}.rmed R ${STUDY_UNITS.result}`,
  ].join('\n');
  return formatExportContent(raw, `${spec.baseName}.export`);
}
