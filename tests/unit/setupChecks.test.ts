import { describe, it, expect } from 'vitest';
import { evaluateSetup, isNativeRunAlias, type SetupInput } from '../../src/setupChecks';

const base: SetupInput = {
  pythonOk: true,
  pythonMissing: [],
  pythonMedcouplingUnavailable: false,
  ruffOk: true,
  dockerOk: false,
  caveOk: false,
  installedVersions: [],
  currentVersion: null,
  bundledVersion: '16.7',
  runAlias: 'cave run',
  userCatalogPath: null,
  userCatalogVersion: null,
};

const byLabel = (rows: ReturnType<typeof evaluateSetup>, label: string) =>
  rows.find((r) => r.label === label)!;

describe('isNativeRunAlias', () => {
  it('treats anything not starting with cave as a native install', () => {
    expect(isNativeRunAlias('cave run')).toBe(false);
    expect(isNativeRunAlias('  Cave run --foo')).toBe(false);
    expect(isNativeRunAlias('run_aster')).toBe(true);
    expect(isNativeRunAlias('/opt/aster/bin/run_aster')).toBe(true);
  });
});

describe('evaluateSetup', () => {
  it('flags Docker, cave and the image as warnings for the cave workflow', () => {
    const rows = evaluateSetup(base);
    expect(byLabel(rows, 'Docker')).toMatchObject({ status: 'warn', passed: false });
    expect(byLabel(rows, 'cave')).toMatchObject({ status: 'warn', passed: false });
    expect(byLabel(rows, 'code_aster version')).toMatchObject({
      status: 'warn',
      description: 'no image installed',
      action: 'installVersion',
    });
    expect(rows.filter((r) => r.passed)).toHaveLength(2);
  });

  it('marks Docker and cave as not needed with a native run alias', () => {
    const rows = evaluateSetup({ ...base, runAlias: 'run_aster' });
    expect(byLabel(rows, 'Docker')).toMatchObject({ status: 'info', passed: true });
    expect(byLabel(rows, 'cave')).toMatchObject({
      status: 'info',
      passed: true,
      description: 'not needed with run alias "run_aster"',
    });
    // No catalog configured yet: nudge toward asterCatalogPath, not toward an image.
    expect(byLabel(rows, 'code_aster version')).toMatchObject({
      status: 'warn',
      passed: false,
      action: 'setCatalogPath',
    });
  });

  it('passes fully with a native alias and a valid catalog path', () => {
    const rows = evaluateSetup({
      ...base,
      runAlias: 'run_aster',
      userCatalogPath: '/opt/aster/lib/aster/code_aster',
      userCatalogVersion: '17.1',
    });
    expect(rows.every((r) => r.passed)).toBe(true);
    expect(byLabel(rows, 'code_aster version')).toMatchObject({
      status: 'ok',
      description: '17.1 (asterCatalogPath)',
    });
  });

  it('prefers the user catalog over a selected cave version', () => {
    const rows = evaluateSetup({
      ...base,
      dockerOk: true,
      caveOk: true,
      installedVersions: ['16.7'],
      currentVersion: '16.7',
      userCatalogPath: '/opt/aster/lib/aster/code_aster',
    });
    expect(byLabel(rows, 'code_aster version').description).toBe('local (asterCatalogPath)');
  });

  it('reports a missing ruff as optional info that still passes', () => {
    const row = byLabel(evaluateSetup({ ...base, ruffOk: false }), 'ruff (formatter)');
    expect(row).toMatchObject({ status: 'info', passed: true });
  });
});
