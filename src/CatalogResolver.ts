import * as vscode from 'vscode';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { spawn } from 'child_process';

const LOG_PREFIX = '[catalog]';
const IMAGE_PREFIX = 'simvia/code_aster';

export type CatalogSource = 'user-setting' | 'cave' | 'vendored';

export interface ResolvedCatalog {
  path: string | null;
  source: CatalogSource;
  version: string | null;
  reason?: string;
}

let channel: vscode.OutputChannel | undefined;

function log(line: string) {
  if (!channel) {
    channel = vscode.window.createOutputChannel('VS Code Aster — Catalog');
  }
  const stamp = new Date().toISOString().slice(11, 23);
  channel.appendLine(`${stamp} ${LOG_PREFIX} ${line}`);
}

export function getCatalogChannel(): vscode.OutputChannel {
  if (!channel) {
    channel = vscode.window.createOutputChannel('VS Code Aster — Catalog');
  }
  return channel;
}

export function cacheRoot(): string {
  return path.join(os.homedir(), '.cache', 'vs-code-aster', 'catalogs');
}

export function caveFilePath(): string {
  return path.join(os.homedir(), '.cave');
}

export function getSelectedCaveVersion(): string | null {
  try {
    const raw = fs.readFileSync(caveFilePath(), 'utf8').trim();
    return raw || null;
  } catch {
    return null;
  }
}

let bundledVersionCache: string | null | undefined;

/**
 * Read the vendored catalog's version string (e.g. "16.7") from
 * `python/asterstudy/code_aster_version/code_aster/Cata/aster_version.py`.
 * Extension context is needed because the path is relative to the installed
 * extension directory. Result is cached — the file is shipped with the
 * extension and doesn't change at runtime.
 */
export function getBundledVersion(context: vscode.ExtensionContext): string | null {
  if (bundledVersionCache !== undefined) {
    return bundledVersionCache;
  }
  try {
    const file = context.asAbsolutePath(
      path.join(
        'python',
        'asterstudy',
        'code_aster_version',
        'code_aster',
        'Cata',
        'aster_version.py'
      )
    );
    const txt = fs.readFileSync(file, 'utf8');
    const m = txt.match(/\*\[\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/);
    if (!m) {
      bundledVersionCache = null;
    } else {
      const [maj, min, patch] = [m[1], m[2], m[3]];
      bundledVersionCache = patch === '0' ? `${maj}.${min}` : `${maj}.${min}.${patch}`;
    }
  } catch {
    bundledVersionCache = null;
  }
  return bundledVersionCache;
}

function run(
  cmd: string,
  args: string[],
  timeoutMs = 60_000
): Promise<{ code: number; stdout: string; stderr: string }> {
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

async function dockerAvailable(): Promise<boolean> {
  const r = await run('docker', ['version', '--format', '{{.Server.Version}}'], 5_000);
  return r.code === 0;
}

async function imagePresent(image: string): Promise<boolean> {
  const r = await run('docker', ['image', 'inspect', image], 10_000);
  return r.code === 0;
}

async function findCataParentInImage(image: string): Promise<string | null> {
  log(`searching Cata directory inside ${image}…`);
  const r = await run(
    'docker',
    [
      'run',
      '--rm',
      '--entrypoint',
      'sh',
      image,
      '-c',
      'find / -name Cata -type d 2>/dev/null; true',
    ],
    30_000
  );
  // `find` often exits 1 on permission-denied entries even with stderr
  // redirected, so rely on stdout rather than the exit code.
  const lines = r.stdout
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean);
  if (lines.length === 0) {
    log(`find produced no output (exit ${r.code}): ${r.stderr.trim().slice(0, 200)}`);
    return null;
  }
  const preferred = lines.find((l) => l.includes('.spack-env/._view')) ?? lines[0];
  if (!preferred) {
    log('no Cata directory found in image');
    return null;
  }
  const parent = path.dirname(preferred);
  log(`found Cata parent = ${parent}`);
  return parent;
}

export async function ensureCatalogExtracted(version: string): Promise<string | null> {
  const versionCache = path.join(cacheRoot(), version);
  const target = path.join(versionCache, 'code_aster');
  if (fs.existsSync(path.join(target, 'Cata'))) {
    log(`cache hit for ${version} → ${target}`);
    return target;
  }

  log(`cache miss for ${version}`);
  if (!(await dockerAvailable())) {
    log('docker is not available');
    return null;
  }
  const image = `${IMAGE_PREFIX}:${version}`;
  if (!(await imagePresent(image))) {
    log(`image ${image} not present locally (skipping auto-pull)`);
    return null;
  }

  const parent = await findCataParentInImage(image);
  if (!parent) {
    return null;
  }

  fs.mkdirSync(versionCache, { recursive: true });

  const statusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 0);
  statusItem.text = `$(sync~spin) Extracting code_aster catalog (${version})…`;
  statusItem.show();

  const t0 = Date.now();
  log(`extracting ${parent} from ${image} → ${versionCache}`);
  const r = await run(
    'docker',
    [
      'run',
      '--rm',
      '--entrypoint',
      'sh',
      '-v',
      `${versionCache}:/out`,
      image,
      '-c',
      `cp -rL '${parent}' /out/code_aster && chown -R $(id -u):$(id -g) /out/code_aster 2>/dev/null || true`,
    ],
    120_000
  );
  statusItem.dispose();
  const dt = ((Date.now() - t0) / 1000).toFixed(1);
  log(`docker run exit ${r.code} in ${dt}s`);
  if (r.code !== 0) {
    log(`extraction stderr: ${r.stderr.trim().slice(0, 400)}`);
    return null;
  }
  if (!fs.existsSync(path.join(target, 'Cata'))) {
    log(`extraction produced no Cata dir at ${target}`);
    return null;
  }
  log(`extracted to ${target}`);
  return target;
}

export async function resolveCatalogPath(): Promise<ResolvedCatalog> {
  log('resolveCatalogPath(): start');

  const userSetting = vscode.workspace
    .getConfiguration('vs-code-aster')
    .get<string>('asterCatalogPath', '')
    .trim();
  if (userSetting) {
    log(`user setting = ${userSetting}`);
    if (fs.existsSync(path.join(userSetting, 'Cata'))) {
      log(`resolved via user-setting → ${userSetting}`);
      return { path: userSetting, source: 'user-setting', version: null };
    }
    log(`user setting path invalid (no Cata/ subdir), ignoring`);
  } else {
    log('user setting not set');
  }

  const version = getSelectedCaveVersion();
  if (!version) {
    log('~/.cave missing or empty');
    notifyFallback('no cave version selected');
    return { path: null, source: 'vendored', version: null, reason: 'no cave version' };
  }
  log(`~/.cave → ${version}`);

  const extracted = await ensureCatalogExtracted(version);
  if (extracted) {
    log(`resolved via cave → ${extracted}`);
    return { path: extracted, source: 'cave', version };
  }

  notifyFallback(`extraction failed for ${version}`);
  return { path: null, source: 'vendored', version, reason: 'extraction failed' };
}

function notifyFallback(reason: string) {
  // Status-bar item already signals the fallback state (warning icon +
  // background + explanatory tooltip). Just log; no toast.
  log(`falling back to vendored catalog (${reason})`);
}

export async function getCatalogInfo(): Promise<string> {
  const resolved = await resolveCatalogPath();
  const lines = [
    `Source: ${resolved.source}`,
    `Version: ${resolved.version ?? '(unknown)'}`,
    `Path: ${resolved.path ?? '(vendored fallback)'}`,
  ];
  if (resolved.reason) {
    lines.push(`Reason: ${resolved.reason}`);
  }
  try {
    const root = cacheRoot();
    if (fs.existsSync(root)) {
      const versions = fs.readdirSync(root);
      lines.push(
        `Cache: ${root} (${versions.length} version(s): ${versions.join(', ') || 'none'})`
      );
    } else {
      lines.push(`Cache: ${root} (empty)`);
    }
  } catch {
    /* ignore */
  }
  return lines.join('\n');
}

export function clearCatalogCache(): void {
  const root = cacheRoot();
  if (fs.existsSync(root)) {
    fs.rmSync(root, { recursive: true, force: true });
    log(`cache cleared: ${root}`);
  }
}

export function clearCatalogCacheFor(version: string): void {
  const dir = path.join(cacheRoot(), version);
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
    log(`cache cleared for ${version}: ${dir}`);
  }
}

/**
 * Remove any catalog cache directory whose version does not appear in the
 * supplied list of currently-installed versions. Called at activation to
 * recover from images removed externally (e.g. `docker rmi` from a terminal).
 */
export function reconcileCatalogCache(installedVersions: string[]): string[] {
  const root = cacheRoot();
  if (!fs.existsSync(root)) {
    return [];
  }
  const installed = new Set(installedVersions);
  const removed: string[] = [];
  for (const entry of fs.readdirSync(root)) {
    if (!installed.has(entry)) {
      fs.rmSync(path.join(root, entry), { recursive: true, force: true });
      removed.push(entry);
    }
  }
  if (removed.length) {
    log(`reconcile removed orphan caches: ${removed.join(', ')}`);
  }
  return removed;
}
