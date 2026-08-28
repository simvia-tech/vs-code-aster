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

  it('handles the Windows MSI layout: codeaster-dist prefix and a bin/run_aster.bat wrapper', () => {
    // Mirrors code_aster-17.4.0-win64.msi: %LOCALAPPDATA%\code_aster\{bin\run_aster.bat, codeaster-dist\...}
    const msiRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'aster-msi-'));
    try {
      const dist = path.join(msiRoot, 'codeaster-dist');
      fs.mkdirSync(path.join(dist, 'lib', 'aster', 'code_aster', 'Cata', 'Commands'), {
        recursive: true,
      });
      fs.mkdirSync(path.join(dist, 'bin'));
      fs.writeFileSync(path.join(dist, 'bin', 'run_aster.bat'), '');
      fs.mkdirSync(path.join(msiRoot, 'bin'));
      fs.writeFileSync(path.join(msiRoot, 'bin', 'run_aster.bat'), '');

      const expectedCatalog = path.join(dist, 'lib', 'aster', 'code_aster');
      expect(findInstallLayout(msiRoot)).toEqual({
        catalogPath: expectedCatalog,
        runCommand: path.join(msiRoot, 'bin', 'run_aster.bat'),
      });
      // Picking the dist folder or the package itself also resolves, and the
      // env wrapper at the root wins over the bare dist launcher.
      const wrapper = path.join(msiRoot, 'bin', 'run_aster.bat');
      expect(findInstallLayout(dist)).toEqual({
        catalogPath: expectedCatalog,
        runCommand: wrapper,
      });
      expect(findInstallLayout(expectedCatalog)).toEqual({
        catalogPath: expectedCatalog,
        runCommand: wrapper,
      });
    } finally {
      fs.rmSync(msiRoot, { recursive: true, force: true });
    }
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
