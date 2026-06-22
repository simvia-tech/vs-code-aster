import { describe, it, expect, afterEach } from 'vitest';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { makeRunLogFilename, pruneRunLogs } from '../../src/projectPaths';

const tmpDirs: string[] = [];
function freshDir(): string {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'vca-runlogs-'));
  tmpDirs.push(d);
  return d;
}

afterEach(() => {
  for (const d of tmpDirs.splice(0)) {
    fs.rmSync(d, { recursive: true, force: true });
  }
});

describe('makeRunLogFilename', () => {
  it('produces a sortable run-<timestamp>.log name', () => {
    expect(makeRunLogFilename()).toMatch(/^run-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.log$/);
  });
});

describe('pruneRunLogs', () => {
  function seed(dir: string, names: string[]) {
    for (const n of names) {
      fs.writeFileSync(path.join(dir, n), 'x');
    }
  }
  function remaining(dir: string): string[] {
    return fs.readdirSync(dir).sort();
  }

  it('keeps only the newest maxKeep logs (lexically newest = latest timestamp)', () => {
    const dir = freshDir();
    seed(dir, [
      'run-2026-06-20T10-00-00.log',
      'run-2026-06-21T10-00-00.log',
      'run-2026-06-22T10-00-00.log',
    ]);
    pruneRunLogs(dir, 2);
    expect(remaining(dir)).toEqual(['run-2026-06-21T10-00-00.log', 'run-2026-06-22T10-00-00.log']);
  });

  it('does nothing when maxKeep <= 0', () => {
    const dir = freshDir();
    seed(dir, ['run-2026-06-20T10-00-00.log']);
    pruneRunLogs(dir, 0);
    expect(remaining(dir)).toHaveLength(1);
  });

  it('ignores non run-*.log files', () => {
    const dir = freshDir();
    seed(dir, ['run-2026-06-20T10-00-00.log', 'notes.txt', 'other.log']);
    pruneRunLogs(dir, 1);
    expect(remaining(dir)).toContain('notes.txt');
    expect(remaining(dir)).toContain('other.log');
    expect(remaining(dir)).toContain('run-2026-06-20T10-00-00.log');
  });
});
