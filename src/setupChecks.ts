/**
 * Pure decision logic behind the sidebar's "Setup (n/N)" group. Kept free of
 * the vscode API so the rules — in particular how a native code_aster install
 * (no Docker, no cave) is recognised — can be unit-tested.
 */

export type SetupStatus = 'ok' | 'warn' | 'info';

export type SetupAction =
  | 'runSetup'
  | 'installVersion'
  | 'selectVersion'
  | 'setCatalogPath'
  | 'setRunAlias';

export interface SetupInput {
  pythonOk: boolean;
  pythonMissing: string[];
  pythonMedcouplingUnavailable: boolean;
  ruffOk: boolean;
  dockerOk: boolean;
  caveOk: boolean;
  installedVersions: string[];
  currentVersion: string | null;
  bundledVersion: string | null;
  /** `vs-code-aster.aliasForRun`, e.g. "cave run" or "run_aster". */
  runAlias: string;
  /** Valid `vs-code-aster.asterCatalogPath` (has a `Cata/` subdir), else null. */
  userCatalogPath: string | null;
  userCatalogVersion: string | null;
}

export interface SetupRow {
  label: string;
  status: SetupStatus;
  description: string;
  tooltip?: string;
  /** Counts toward the n/N title. Optional tools and not-needed steps pass. */
  passed: boolean;
  action: SetupAction;
}

/** Simulations run through something other than cave: a native code_aster. */
export function isNativeRunAlias(alias: string): boolean {
  return !alias.trim().toLowerCase().startsWith('cave');
}

export function evaluateSetup(p: SetupInput): SetupRow[] {
  const nativeRun = isNativeRunAlias(p.runAlias);
  const notNeeded = `not needed with run alias "${p.runAlias.trim()}"`;
  const versionOk = !!p.currentVersion && p.installedVersions.includes(p.currentVersion);

  const python: SetupRow = {
    label: 'Python LSP dependencies',
    status: p.pythonOk ? 'ok' : 'warn',
    description: p.pythonOk
      ? p.pythonMedcouplingUnavailable
        ? 'pygls, numpy installed (medcoupling unavailable on Python 3.14+ — mesh viewer disabled)'
        : 'pygls, numpy, medcoupling installed'
      : `missing: ${p.pythonMissing.join(', ') || '?'}`,
    passed: p.pythonOk,
    action: 'runSetup',
  };

  const ruff: SetupRow = {
    label: 'ruff (formatter)',
    status: p.ruffOk ? 'ok' : 'info',
    description: p.ruffOk ? 'available' : 'not installed (optional)',
    passed: true,
    action: 'runSetup',
  };

  const docker: SetupRow = {
    label: 'Docker',
    status: p.dockerOk ? 'ok' : nativeRun ? 'info' : 'warn',
    description: p.dockerOk ? 'running' : nativeRun ? notNeeded : 'not available',
    passed: p.dockerOk || nativeRun,
    action: nativeRun ? 'setRunAlias' : 'runSetup',
  };

  const cave: SetupRow = {
    label: 'cave',
    status: p.caveOk ? 'ok' : nativeRun ? 'info' : 'warn',
    description: p.caveOk ? 'on PATH' : nativeRun ? notNeeded : 'not installed',
    passed: p.caveOk || nativeRun,
    action: nativeRun ? 'setRunAlias' : 'runSetup',
  };

  let version: SetupRow;
  if (p.userCatalogPath) {
    version = {
      label: 'code_aster version',
      status: 'ok',
      description: `${p.userCatalogVersion ?? 'local'} (asterCatalogPath)`,
      tooltip: `Catalog read from ${p.userCatalogPath}`,
      passed: true,
      action: 'setCatalogPath',
    };
  } else if (versionOk) {
    version = {
      label: 'code_aster version',
      status: 'ok',
      description: `using ${p.currentVersion}`,
      passed: true,
      action: 'selectVersion',
    };
  } else if (nativeRun) {
    version = {
      label: 'code_aster version',
      status: 'warn',
      description: 'click to locate your code_aster install',
      tooltip:
        'Pick your code_aster installation folder: asterCatalogPath (the directory containing ' +
        'Cata/) and aliasForRun (bin/run_aster) are filled in from it. Until then the bundled ' +
        `${p.bundledVersion ?? '?'} catalog is used.`,
      passed: false,
      action: 'setCatalogPath',
    };
  } else if (p.installedVersions.length === 0) {
    version = {
      label: 'code_aster version',
      status: 'warn',
      description: 'no image installed',
      passed: false,
      action: 'installVersion',
    };
  } else {
    version = {
      label: 'code_aster version',
      status: 'warn',
      description: `bundled ${p.bundledVersion ?? '?'} fallback`,
      passed: false,
      action: 'selectVersion',
    };
  }

  return [python, ruff, docker, cave, version];
}
