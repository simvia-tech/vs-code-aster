import * as vscode from 'vscode';
import {
  installLspDeps,
  installRuff,
  probeLspDeps,
  probeRuff,
  resolvePythonExecutable,
  runProc,
} from './PythonEnv';
import { dockerAvailable, getSelectedCaveVersion } from './CatalogResolver';
import { CaveStatusBar, listInstalledVersions } from './CaveStatusBar';
import { LspServer } from './LspServer';

const COMMAND_NAME = 'code_aster: Run setup checks';

const KEY_PYTHON_DEPS = 'setup.pythonDepsDeclined';
const KEY_RUFF = 'formatter.ruffDeclined';
const KEY_DOCKER = 'setup.dockerDeclined';
const KEY_CAVE = 'setup.caveDeclined';
const KEY_CAVE_VERSION = 'setup.caveVersionDeclined';

let runningInSession = false;
let firedThisSession = false;

const CAVE_INSTALL_CMD =
  'sh -c "$(curl -fsSL https://raw.githubusercontent.com/simvia-tech/cave/main/tools/install.sh)"';

/**
 * Walks the user through the setup chain in order:
 *   1. Python LSP deps (pygls, numpy, medcoupling)
 *   2. ruff (formatter)
 *   3. Docker daemon
 *   4. cave on PATH
 *   5. at least one code_aster image
 *
 * Each step is opt-in with three buttons (Install / Not now / Don't ask
 * again). Persisted decisions live in `context.globalState`.
 *
 * Called automatically on first `.comm` / `.export` open per session;
 * also exposed as `vs-code-aster.runSetup` for explicit invocation.
 */
export async function runSetupProbes(
  context: vscode.ExtensionContext,
  options: { force?: boolean } = {}
): Promise<void> {
  if (runningInSession) {
    return;
  }
  if (firedThisSession && !options.force) {
    return;
  }
  runningInSession = true;
  firedThisSession = true;
  try {
    await stepPythonDeps(context, options.force);
    await stepRuff(context, options.force);
    const hasDocker = await stepDocker(context, options.force);
    const hasCave = await stepCave(context, hasDocker, options.force);
    if (hasCave) {
      await stepCaveVersion(context, options.force);
    }
  } finally {
    runningInSession = false;
  }
}

// ---------------- step 1: Python LSP deps ----------------

async function stepPythonDeps(context: vscode.ExtensionContext, force?: boolean) {
  if (!force && context.globalState.get<boolean>(KEY_PYTHON_DEPS)) {
    return;
  }
  const probe = await probeLspDeps(context);
  if (probe.ok) {
    return;
  }
  const choice = await vscode.window.showInformationMessage(
    `code_aster language server needs Python packages (${probe.missing.join(', ')}). ` +
      'Install them now? They will go into a managed virtual environment owned by the extension.',
    'Install',
    'Not now',
    "Don't ask again"
  );
  if (choice === "Don't ask again") {
    await context.globalState.update(KEY_PYTHON_DEPS, true);
    return;
  }
  if (choice !== 'Install') {
    return;
  }
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Installing code_aster LSP dependencies…',
      cancellable: false,
    },
    async (progress) => {
      const result = await installLspDeps(context, progress);
      if (!result.ok) {
        const action = await vscode.window.showErrorMessage(
          `Could not install LSP deps: ${result.error ?? 'unknown error'}`,
          'Retry',
          'Open README'
        );
        if (action === 'Retry') {
          await stepPythonDeps(context, true);
        } else if (action === 'Open README') {
          void vscode.env.openExternal(
            vscode.Uri.parse('https://github.com/simvia-tech/vs-code-aster#installation')
          );
        }
        return;
      }
      vscode.window.showInformationMessage(
        'code_aster LSP dependencies installed. Restarting language server…'
      );
      void LspServer.instance.restart();
    }
  );
}

// ---------------- step 2: ruff ----------------

async function stepRuff(context: vscode.ExtensionContext, force?: boolean) {
  if (!force && context.globalState.get<boolean>(KEY_RUFF)) {
    return;
  }
  const config = vscode.workspace.getConfiguration('vs-code-aster');
  if ((config.get<string>('formatter') || 'ruff').trim() !== 'ruff') {
    return; // user picked a different formatter, nothing to install.
  }
  if (await probeRuff(context)) {
    return;
  }
  const choice = await vscode.window.showInformationMessage(
    'Install `ruff` to enable code_aster file formatting?',
    'Install',
    'Not now',
    "Don't ask again"
  );
  if (choice === "Don't ask again") {
    await context.globalState.update(KEY_RUFF, true);
    return;
  }
  if (choice !== 'Install') {
    return;
  }
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Installing ruff…',
      cancellable: false,
    },
    async (progress) => {
      const result = await installRuff(context, progress);
      if (!result.ok) {
        vscode.window.showErrorMessage(
          `Could not install ruff: ${result.error ?? 'unknown error'}`
        );
        return;
      }
      vscode.window.showInformationMessage('ruff installed. Formatting is ready.');
    }
  );
}

// ---------------- step 3: Docker ----------------

async function stepDocker(context: vscode.ExtensionContext, force?: boolean): Promise<boolean> {
  if (await dockerAvailable()) {
    return true;
  }
  if (!force && context.globalState.get<boolean>(KEY_DOCKER)) {
    return false;
  }
  const choice = await vscode.window.showInformationMessage(
    'Docker is required to install cave and run code_aster simulations. ' + 'Install it now?',
    'Install',
    'Not now',
    "Don't ask again"
  );
  if (choice === "Don't ask again") {
    await context.globalState.update(KEY_DOCKER, true);
    return false;
  }
  if (choice === 'Install') {
    void vscode.env.openExternal(vscode.Uri.parse('https://docs.docker.com/get-docker/'));
  }
  return false;
}

// ---------------- step 4: cave ----------------

async function caveOnPath(): Promise<boolean> {
  const r = await runProc(process.platform === 'win32' ? 'where' : 'which', ['cave'], 3_000);
  return r.code === 0;
}

async function stepCave(
  context: vscode.ExtensionContext,
  hasDocker: boolean,
  force?: boolean
): Promise<boolean> {
  if (await caveOnPath()) {
    return true;
  }
  if (!hasDocker) {
    return false; // Docker step already declined / unavailable; don't pile on.
  }
  if (!force && context.globalState.get<boolean>(KEY_CAVE)) {
    return false;
  }

  // Native Windows: no install script. Open instructions instead.
  if (process.platform === 'win32') {
    const choice = await vscode.window.showInformationMessage(
      'cave (the code_aster version manager) is not installed.',
      'Open install instructions',
      "Don't ask again"
    );
    if (choice === "Don't ask again") {
      await context.globalState.update(KEY_CAVE, true);
    } else if (choice === 'Open install instructions') {
      void vscode.env.openExternal(
        vscode.Uri.parse('https://github.com/simvia-tech/cave#installation')
      );
    }
    return false;
  }

  const choice = await vscode.window.showInformationMessage(
    'Docker is set up. Install cave to manage code_aster versions? ' +
      'This runs an install script with `sudo`.',
    'Install',
    'Show me the command',
    'Not now',
    "Don't ask again"
  );
  if (choice === "Don't ask again") {
    await context.globalState.update(KEY_CAVE, true);
    return false;
  }
  if (choice === 'Show me the command') {
    await vscode.window.showInformationMessage(
      `cave install command:\n\n${CAVE_INSTALL_CMD}`,
      { modal: true },
      'OK'
    );
    return false;
  }
  if (choice !== 'Install') {
    return false;
  }

  const term = vscode.window.createTerminal({ name: 'cave install' });
  term.show();
  term.sendText(CAVE_INSTALL_CMD);

  // Poll for cave to appear on PATH (up to 5 minutes).
  return await pollForCave();
}

async function pollForCave(): Promise<boolean> {
  const deadline = Date.now() + 5 * 60_000;
  while (Date.now() < deadline) {
    if (await caveOnPath()) {
      return true;
    }
    await new Promise((r) => setTimeout(r, 2_000));
  }
  return false;
}

// ---------------- step 5: code_aster image ----------------

async function stepCaveVersion(context: vscode.ExtensionContext, force?: boolean): Promise<void> {
  if (!force && context.globalState.get<boolean>(KEY_CAVE_VERSION)) {
    return;
  }
  // Already have a selection AND the image is present? skip.
  const selected = getSelectedCaveVersion();
  const installed = await listInstalledVersions();
  if (selected && installed.includes(selected)) {
    return;
  }
  if (installed.length > 0 && !selected) {
    // Image present but ~/.cave is empty — let the picker handle it,
    // but don't be pushy.
  }

  const choice = await vscode.window.showInformationMessage(
    'cave is set up. Install a code_aster version to enable simulations?',
    'Install version…',
    'Not now',
    "Don't ask again"
  );
  if (choice === "Don't ask again") {
    await context.globalState.update(KEY_CAVE_VERSION, true);
    return;
  }
  if (choice !== 'Install version…') {
    return;
  }
  await CaveStatusBar.instance.openInstallVersion();
}
