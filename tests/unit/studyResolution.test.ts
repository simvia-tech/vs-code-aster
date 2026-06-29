import { describe, it, expect } from 'vitest';
import { commNameFromExport, exportReferencesComm } from '../../src/studyResolution';

const EXPORT = [
  'P actions make_etude',
  'F comm case.comm D 1',
  'F mmed mesh.med D 20',
  'F mess case.mess R 6',
  'F rmed result.rmed R 80',
].join('\n');

describe('commNameFromExport', () => {
  it('extracts the comm file name from the F comm line', () => {
    expect(commNameFromExport(EXPORT)).toBe('case.comm');
  });

  it('preserves the full path when the path is absolute', () => {
    expect(commNameFromExport('F comm /tmp/study/run.comm D 1')).toBe('/tmp/study/run.comm');
  });

  it('preserves the relative path when the comm is in a subdirectory', () => {
    expect(commNameFromExport('F comm subdir/run.comm D 1')).toBe('subdir/run.comm');
  });

  it('ignores comment lines', () => {
    expect(commNameFromExport('# F comm case.comm D 1')).toBeUndefined();
  });

  it('returns undefined when there is no comm declaration', () => {
    expect(commNameFromExport('F mmed mesh.med D 20')).toBeUndefined();
  });
});

describe('exportReferencesComm', () => {
  it('matches on the declared comm file name', () => {
    expect(exportReferencesComm(EXPORT, 'case.comm')).toBe(true);
  });

  it('matches loosely when the comm name appears anywhere', () => {
    expect(exportReferencesComm('F mmed case.med D 20', 'case.med')).toBe(true);
  });

  it('does not match an unrelated study', () => {
    expect(exportReferencesComm(EXPORT, 'other.comm')).toBe(false);
  });
});
