import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface InstallLayout {
  /** The `code_aster` Python package (contains `Cata/Commands`), or null. */
  catalogPath: string | null;
  /** Full path of the study launcher (`bin/run_aster` or a Windows variant), or null. */
  runCommand: string | null;
}

const RUN_ASTER_NAMES =
  process.platform === 'win32'
    ? ['run_aster.bat', 'run_aster.cmd', 'run_aster.exe', 'run_aster']
    : ['run_aster', 'run_aster.bat', 'run_aster.cmd', 'run_aster.exe'];

/**
 * Derive both settings from a folder the user picked. Accepts the install
 * root (`<prefix>` holding `lib/aster/code_aster` and `bin/run_aster`),
 * `lib/aster`, or the `code_aster` package itself: the search walks up to
 * three levels so a folder picked too deep still resolves.
 */
export function findInstallLayout(picked: string): InstallLayout {
  const isCatalog = (dir: string) => fs.existsSync(path.join(dir, 'Cata', 'Commands'));
  let catalogPath: string | null = null;
  let runCommand: string | null = null;
  let dir = picked;
  for (let depth = 0; depth < 4; depth++) {
    if (!catalogPath) {
      catalogPath =
        [dir, path.join(dir, 'code_aster'), path.join(dir, 'lib', 'aster', 'code_aster')].find(
          isCatalog
        ) ?? null;
    }
    if (!runCommand) {
      runCommand =
        RUN_ASTER_NAMES.map((n) => path.join(dir, 'bin', n)).find((p) => fs.existsSync(p)) ?? null;
    }
    const parent = path.dirname(dir);
    if ((catalogPath && runCommand) || parent === dir) {
      break;
    }
    dir = parent;
  }
  return { catalogPath, runCommand };
}

/** Make a launcher path usable as the first word of `aliasForRun` in the user's shell. */
export function quoteRunCommand(cmd: string, platform: NodeJS.Platform = process.platform): string {
  if (!/\s/.test(cmd)) {
    return cmd;
  }
  // PowerShell needs the call operator to run a quoted path.
  return platform === 'win32' ? `& "${cmd}"` : `"${cmd}"`;
}

/**
 * `vs-code-aster.locateInstall`: folder picker that fills `asterCatalogPath`
 * and `aliasForRun` from a native code_aster installation.
 */
export async function locateCodeAsterInstall(): Promise<void> {
  const picked = await vscode.window.showOpenDialog({
    canSelectFiles: false,
    canSelectFolders: true,
    canSelectMany: false,
    title: 'Select your code_aster installation folder',
    openLabel: 'Use this code_aster install',
  });
  if (!picked || picked.length === 0) {
    return;
  }
  const layout = findInstallLayout(picked[0].fsPath);
  if (!layout.catalogPath && !layout.runCommand) {
    const choice = await vscode.window.showErrorMessage(
      `No code_aster install found under ${picked[0].fsPath}: expected ` +
        '`lib/aster/code_aster/Cata` and `bin/run_aster`. Pick the install root, or set the ' +
        'settings by hand.',
      'Open settings'
    );
    if (choice === 'Open settings') {
      void vscode.commands.executeCommand(
        'workbench.action.openSettings',
        '@ext:simvia.vs-code-aster'
      );
    }
    return;
  }

  const cfg = vscode.workspace.getConfiguration('vs-code-aster');
  const done: string[] = [];
  if (layout.catalogPath) {
    await cfg.update('asterCatalogPath', layout.catalogPath, vscode.ConfigurationTarget.Global);
    done.push(`catalog: ${layout.catalogPath}`);
  }
  if (layout.runCommand) {
    const alias = quoteRunCommand(layout.runCommand);
    await cfg.update('aliasForRun', alias, vscode.ConfigurationTarget.Global);
    done.push(`run command: ${alias}`);
  }
  const missing = !layout.catalogPath
    ? 'No `Cata/` catalog found there; language features keep the bundled catalog.'
    : !layout.runCommand
      ? 'No `bin/run_aster` found there; set `aliasForRun` to your launch command by hand.'
      : '';

  if (layout.catalogPath) {
    // Via the command rather than importing LspServer: that module pulls in
    // vscode-languageclient, which this unit-testable file must stay clear of.
    void vscode.commands.executeCommand('vs-code-aster.restartLSPServer');
  }
  const choice = await vscode.window.showInformationMessage(
    `code_aster install configured (${done.join(', ')}). ${missing}`.trim(),
    ...(missing ? ['Open settings'] : [])
  );
  if (choice === 'Open settings') {
    void vscode.commands.executeCommand(
      'workbench.action.openSettings',
      '@ext:simvia.vs-code-aster'
    );
  }
}
