import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { findInstallLayout, quoteRunCommand } from '../../src/LocateInstall';

let root: string;

beforeAll(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), 'aster-install-'));
  fs.mkdirSync(path.join(root, 'lib', 'aster', 'code_aster', 'Cata', 'Commands'), {
    recursive: true,
  });
  fs.mkdirSync(path.join(root, 'bin'));
  fs.writeFileSync(path.join(root, 'bin', 'run_aster'), '#!/bin/sh\n');
});

afterAll(() => {
  fs.rmSync(root, { recursive: true, force: true });
});

describe('findInstallLayout', () => {
  const expected = () => ({
    catalogPath: path.join(root, 'lib', 'aster', 'code_aster'),
    runCommand: path.join(root, 'bin', 'run_aster'),
  });

  it('derives both settings from the install root', () => {
    expect(findInstallLayout(root)).toEqual(expected());
  });

  it('accepts the code_aster package itself and walks up to find bin/', () => {
    expect(findInstallLayout(path.join(root, 'lib', 'aster', 'code_aster'))).toEqual(expected());
  });

  it('accepts lib/aster', () => {
    expect(findInstallLayout(path.join(root, 'lib', 'aster'))).toEqual(expected());
  });

  it('returns nulls for an unrelated folder', () => {
    expect(findInstallLayout(os.tmpdir())).toEqual({ catalogPath: null, runCommand: null });
  });
});

describe('quoteRunCommand', () => {
  it('leaves paths without whitespace alone', () => {
    expect(quoteRunCommand('/opt/aster/bin/run_aster', 'linux')).toBe('/opt/aster/bin/run_aster');
  });

  it('quotes paths with spaces, with the PowerShell call operator on Windows', () => {
    expect(quoteRunCommand('/opt/my aster/bin/run_aster', 'linux')).toBe(
      '"/opt/my aster/bin/run_aster"'
    );
    expect(quoteRunCommand('D:\\code aster\\bin\\run_aster.bat', 'win32')).toBe(
      '& "D:\\code aster\\bin\\run_aster.bat"'
    );
  });
});
