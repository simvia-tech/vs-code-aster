import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

const ROOT_NAME = '.vs-code-aster';
const LEGACY_VISU_DATA = '.visu_data';
const LEGACY_RUN_LOG = '.vscode-aster-run.log';

function ensureDir(dir: string): string {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  return dir;
}

/**
 * Project root = the directory passed in. Each project folder gets its own
 * `.vs-code-aster/` tree; we never walk up to a workspace-wide dir.
 */
export function getProjectDir(projectDir: string): string {
  return ensureDir(path.join(projectDir, ROOT_NAME));
}

export function getMeshCacheDir(projectDir: string): string {
  const dir = ensureDir(path.join(getProjectDir(projectDir), 'mesh_cache'));
  migrateLegacyMeshCache(projectDir, dir);
  return dir;
}

export function getScreenshotsDir(projectDir: string): string {
  return ensureDir(path.join(getProjectDir(projectDir), 'screenshots'));
}

export function getRunLogsDir(projectDir: string): string {
  const dir = ensureDir(path.join(getProjectDir(projectDir), 'run_logs'));
  migrateLegacyRunLog(projectDir, dir);
  return dir;
}

function migrateLegacyMeshCache(projectDir: string, newDir: string): void {
  const legacy = path.join(projectDir, LEGACY_VISU_DATA);
  if (!fs.existsSync(legacy)) {
    return;
  }
  try {
    for (const entry of fs.readdirSync(legacy)) {
      const from = path.join(legacy, entry);
      const to = path.join(newDir, entry);
      if (!fs.existsSync(to)) {
        fs.renameSync(from, to);
      } else {
        fs.rmSync(from, { recursive: true, force: true });
      }
    }
    fs.rmdirSync(legacy);
    vscode.window.showInformationMessage(
      `Migrated ${LEGACY_VISU_DATA}/ to ${ROOT_NAME}/mesh_cache/ in ${projectDir}`
    );
  } catch (err) {
    console.error(`[projectPaths] Failed to migrate ${legacy}:`, err);
  }
}

function migrateLegacyRunLog(projectDir: string, runLogsDir: string): void {
  const legacy = path.join(projectDir, LEGACY_RUN_LOG);
  if (!fs.existsSync(legacy)) {
    return;
  }
  try {
    const mtime = fs.statSync(legacy).mtime;
    const stamp = mtime.toISOString().replace(/[:.]/g, '-').slice(0, 19);
    let target = path.join(runLogsDir, `run-${stamp}.log`);
    let suffix = 1;
    while (fs.existsSync(target)) {
      target = path.join(runLogsDir, `run-${stamp}-${suffix}.log`);
      suffix++;
    }
    fs.renameSync(legacy, target);
    vscode.window.showInformationMessage(
      `Migrated ${LEGACY_RUN_LOG} to ${ROOT_NAME}/run_logs/${path.basename(target)} in ${projectDir}`
    );
  } catch (err) {
    console.error(`[projectPaths] Failed to migrate ${legacy}:`, err);
  }
}

export function pruneRunLogs(runLogsDir: string, maxKeep: number): void {
  if (maxKeep <= 0) {
    return;
  }
  try {
    const entries = fs
      .readdirSync(runLogsDir)
      .filter((f) => f.startsWith('run-') && f.endsWith('.log'))
      .map((f) => ({ name: f, full: path.join(runLogsDir, f) }))
      .sort((a, b) => a.name.localeCompare(b.name));
    const toDelete = entries.slice(0, Math.max(0, entries.length - maxKeep));
    for (const e of toDelete) {
      fs.unlinkSync(e.full);
    }
  } catch (err) {
    console.error(`[projectPaths] Failed to prune run logs in ${runLogsDir}:`, err);
  }
}

export function makeRunLogFilename(): string {
  const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  return `run-${stamp}.log`;
}
