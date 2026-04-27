import * as vscode from 'vscode';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { spawn } from 'child_process';

export const LSP_DEPS = ['pygls==1.3.1', 'numpy', 'medcoupling'] as const;

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

/** Probe the LSP's three Python deps via the configured interpreter. */
export async function probeLspDeps(
  context: vscode.ExtensionContext
): Promise<{ ok: boolean; missing: string[] }> {
  const python = resolvePythonExecutable(context);
  const r = await runProc(python, ['-c', 'import pygls, numpy, medcoupling'], 8_000);
  if (r.code === 0) {
    return { ok: true, missing: [] };
  }
  // Parse the ImportError message to figure out which package is missing.
  const m = r.stderr.match(/No module named ['"]([^'"]+)['"]/);
  const missing = m ? [m[1]] : [...LSP_DEPS];
  return { ok: false, missing };
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
): Promise<{ ok: boolean; pythonPath: string; error?: string }> {
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

  progress.report({ message: 'Upgrading pip…' });
  await runProc(pythonPath, ['-m', 'pip', 'install', '--upgrade', 'pip'], 60_000);

  progress.report({ message: `Installing ${LSP_DEPS.join(', ')}…` });
  let r = await runProc(pythonPath, ['-m', 'pip', 'install', ...LSP_DEPS], 240_000);
  if (r.code !== 0 && /externally[- ]managed/i.test(r.stderr)) {
    progress.report({ message: 'Retrying with --user (externally-managed env)…' });
    r = await runProc(pythonPath, ['-m', 'pip', 'install', '--user', ...LSP_DEPS], 240_000);
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

  return { ok: true, pythonPath };
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
