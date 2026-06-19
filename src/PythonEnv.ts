import * as vscode from 'vscode';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { spawn } from 'child_process';

export const LSP_DEPS = ['pygls==1.3.1', 'numpy', 'medcoupling'] as const;

// medcoupling publishes prebuilt wheels for CPython 3.9–3.13 only (no cp314 yet).
// On newer interpreters pip falls back to a source build that needs cmake + a
// full toolchain and fails; we skip it instead and run without the mesh viewer.
export const MEDCOUPLING_MAX_MINOR = 13;

/** LSP deps that ship wheels for every supported Python (everything but medcoupling). */
export const CORE_LSP_DEPS = ['pygls==1.3.1', 'numpy'] as const;

const MEDCOUPLING_WARNING =
  'medcoupling has no prebuilt wheel for Python 3.14+ yet, so it was skipped. ' +
  'The language server works, but the .med mesh viewer is unavailable — ' +
  'use a Python 3.10–3.13 interpreter for full functionality.';

export interface RunResult {
  code: number;
  stdout: string;
  stderr: string;
}

export function runProc(cmd: string, args: string[], timeoutMs = 60_000): Promise<RunResult> {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill('SIGKILL'), timeoutMs);
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('error', (err) => {
      clearTimeout(timer);
      resolve({ code: -1, stdout, stderr: stderr + String(err) });
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code: code ?? -1, stdout, stderr });
    });
  });
}

/** Query an interpreter's (major, minor) version, or null if it can't be run. */
export async function pythonVersion(python: string): Promise<[number, number] | null> {
  const r = await runProc(
    python,
    ['-c', 'import sys;print(sys.version_info[0], sys.version_info[1])'],
    5_000
  );
  if (r.code !== 0) {
    return null;
  }
  const m = r.stdout.trim().match(/^(\d+)\s+(\d+)/);
  return m ? [Number(m[1]), Number(m[2])] : null;
}

/** True when this interpreter is too new for a prebuilt medcoupling wheel. */
export function medcouplingUnavailable(v: [number, number] | null): boolean {
  return !!v && (v[0] > 3 || (v[0] === 3 && v[1] > MEDCOUPLING_MAX_MINOR));
}

/**
 * Resolve the Python interpreter the LSP should use. Order:
 *   1. user-set `vs-code-aster.pythonExecutablePath` (anything other than
 *      the literal default `python3`),
 *   2. our managed venv at `<globalStorageUri>/.venv`,
 *   3. fall back to `python3` (so the extension can at least boot).
 */
export function resolvePythonExecutable(context: vscode.ExtensionContext): string {
  const config = vscode.workspace.getConfiguration('vs-code-aster');
  const userSetting = (config.get<string>('pythonExecutablePath') || '').trim();
  if (userSetting && userSetting !== 'python3') {
    return userSetting;
  }
  const managed = managedVenvPython(context);
  if (managed && fs.existsSync(managed)) {
    return managed;
  }
  return 'python3';
}

export function managedVenvDir(context: vscode.ExtensionContext): string {
  return path.join(context.globalStorageUri.fsPath, '.venv');
}

export function managedVenvPython(context: vscode.ExtensionContext): string {
  const dir = managedVenvDir(context);
  return process.platform === 'win32'
    ? path.join(dir, 'Scripts', 'python.exe')
    : path.join(dir, 'bin', 'python');
}

/**
 * "Has the user explicitly chosen an interpreter?" Used to decide
 * whether auto-installing into a managed venv would override their
 * choice.
 */
export function userHasCustomPython(): boolean {
  const userSetting = (
    vscode.workspace.getConfiguration('vs-code-aster').get<string>('pythonExecutablePath') || ''
  ).trim();
  return userSetting !== '' && userSetting !== 'python3';
}

export interface DepsProbe {
  /** True when everything required for the current interpreter is importable. */
  ok: boolean;
  /** Packages we want but couldn't import. */
  missing: string[];
  /** Interpreter is too new for a medcoupling wheel; it's treated as optional. */
  medcouplingUnavailable: boolean;
  pythonVersion: [number, number] | null;
}

/**
 * Probe the LSP's Python deps via the configured interpreter. On interpreters
 * too new for a medcoupling wheel (Python 3.14+), medcoupling is optional: `ok`
 * only requires pygls + numpy, so we don't nag to install something that can't
 * install.
 */
export async function probeLspDeps(context: vscode.ExtensionContext): Promise<DepsProbe> {
  const python = resolvePythonExecutable(context);
  const v = await pythonVersion(python);
  const noMedcoupling = medcouplingUnavailable(v);
  const imports = noMedcoupling ? 'import pygls, numpy' : 'import pygls, numpy, medcoupling';
  const r = await runProc(python, ['-c', imports], 8_000);
  if (r.code === 0) {
    return { ok: true, missing: [], medcouplingUnavailable: noMedcoupling, pythonVersion: v };
  }
  // Parse the ImportError message to figure out which package is missing.
  const m = r.stderr.match(/No module named ['"]([^'"]+)['"]/);
  const missing = m ? [m[1]] : noMedcoupling ? [...CORE_LSP_DEPS] : [...LSP_DEPS];
  return { ok: false, missing, medcouplingUnavailable: noMedcoupling, pythonVersion: v };
}

/** Probe ruff via the configured interpreter. Reused by CommFormatter. */
export async function probeRuff(context: vscode.ExtensionContext): Promise<boolean> {
  const python = resolvePythonExecutable(context);
  const r = await runProc(python, ['-m', 'ruff', '--version'], 5_000);
  return r.code === 0;
}

async function findBootstrapPython(): Promise<string | null> {
  const candidates =
    process.platform === 'win32' ? ['py', 'python', 'python3'] : ['python3', 'python'];
  for (const c of candidates) {
    const r = await runProc(c, ['-c', 'import sys; print(sys.version_info[:2])'], 4_000);
    if (r.code === 0) {
      return c;
    }
  }
  return null;
}

/**
 * Create the managed venv if missing. Returns the absolute path of the
 * venv's Python interpreter, or null on failure.
 */
export async function ensureManagedVenv(context: vscode.ExtensionContext): Promise<string | null> {
  const venvPython = managedVenvPython(context);
  if (fs.existsSync(venvPython)) {
    return venvPython;
  }
  fs.mkdirSync(context.globalStorageUri.fsPath, { recursive: true });
  const bootstrap = await findBootstrapPython();
  if (!bootstrap) {
    return null;
  }
  const r = await runProc(bootstrap, ['-m', 'venv', managedVenvDir(context)], 60_000);
  if (r.code !== 0) {
    return null;
  }
  return fs.existsSync(venvPython) ? venvPython : null;
}

/**
 * Install the LSP deps into the user's chosen interpreter (if they set
 * one) or into the managed venv. Surfaces progress through the supplied
 * progress reporter.
 */
export async function installLspDeps(
  context: vscode.ExtensionContext,
  progress: vscode.Progress<{ message?: string }>
): Promise<{ ok: boolean; pythonPath: string; error?: string; warning?: string }> {
  let pythonPath: string;
  if (userHasCustomPython()) {
    pythonPath = resolvePythonExecutable(context);
  } else {
    progress.report({ message: 'Creating managed venv…' });
    const venvPython = await ensureManagedVenv(context);
    if (!venvPython) {
      return {
        ok: false,
        pythonPath: '',
        error:
          'Could not create a managed Python venv (is `python -m venv` available on this system?).',
      };
    }
    pythonPath = venvPython;
  }

  // On Python 3.14+ medcoupling has no wheel and a source build fails on most
  // machines; install only the wheel-backed deps so the LSP still works.
  const skipMedcoupling = medcouplingUnavailable(await pythonVersion(pythonPath));
  const deps = skipMedcoupling ? [...CORE_LSP_DEPS] : [...LSP_DEPS];

  progress.report({ message: 'Upgrading pip…' });
  await runProc(pythonPath, ['-m', 'pip', 'install', '--upgrade', 'pip'], 60_000);

  progress.report({ message: `Installing ${deps.join(', ')}…` });
  let r = await runProc(pythonPath, ['-m', 'pip', 'install', ...deps], 240_000);
  if (r.code !== 0 && /externally[- ]managed/i.test(r.stderr)) {
    progress.report({ message: 'Retrying with --user (externally-managed env)…' });
    r = await runProc(pythonPath, ['-m', 'pip', 'install', '--user', ...deps], 240_000);
  }
  if (r.code !== 0) {
    return {
      ok: false,
      pythonPath,
      error: r.stderr.trim().split('\n').slice(-1)[0] || `pip exit ${r.code}`,
    };
  }

  // If we used the managed venv, write its path back to the setting so
  // subsequent sessions skip the bootstrap entirely.
  if (!userHasCustomPython()) {
    await vscode.workspace
      .getConfiguration('vs-code-aster')
      .update('pythonExecutablePath', pythonPath, vscode.ConfigurationTarget.Global);
  }

  return { ok: true, pythonPath, warning: skipMedcoupling ? MEDCOUPLING_WARNING : undefined };
}

/** Install ruff into the same interpreter the LSP uses. */
export async function installRuff(
  context: vscode.ExtensionContext,
  progress: vscode.Progress<{ message?: string }>
): Promise<{ ok: boolean; error?: string }> {
  // Make sure we have a venv to install into; otherwise share the user's.
  if (!userHasCustomPython()) {
    const venv = await ensureManagedVenv(context);
    if (!venv) {
      return { ok: false, error: 'Managed venv unavailable.' };
    }
  }
  const python = resolvePythonExecutable(context);
  progress.report({ message: `${python} -m pip install ruff` });
  let r = await runProc(python, ['-m', 'pip', 'install', 'ruff'], 120_000);
  if (r.code !== 0 && /externally[- ]managed/i.test(r.stderr)) {
    r = await runProc(python, ['-m', 'pip', 'install', '--user', 'ruff'], 120_000);
  }
  if (r.code !== 0) {
    return {
      ok: false,
      error: r.stderr.trim().split('\n').slice(-1)[0] || `pip exit ${r.code}`,
    };
  }
  return { ok: true };
}

/** Used by readme-style messaging. Hides $HOME for prettier display. */
export function prettyPath(p: string): string {
  const home = os.homedir();
  return p.startsWith(home) ? '~' + p.slice(home.length) : p;
}
