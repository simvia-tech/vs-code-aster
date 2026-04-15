/**
 * Helpers for recognizing MED mesh files without relying on extension alone.
 *
 * MED files are HDF5 files, and HDF5 files start with a fixed 8-byte magic
 * signature. This module uses that to:
 *  1. Detect when a user opens a file that looks like MED (auto-prompt).
 *  2. Provide a command that adds the active file's extension to the MED
 *     list and re-opens the file in the mesh viewer.
 *
 * The prompt can be silenced per-extension by the user via the "Don't ask for
 * .xx" option, which persists in `globalState`.
 */
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { MedEditorProvider, STATIC_MED_EXTS } from './MedEditorProvider';

const HDF5_MAGIC = Buffer.from([0x89, 0x48, 0x44, 0x46, 0x0d, 0x0a, 0x1a, 0x0a]);
const DECLINED_EXTS_KEY = 'declinedMedExtensions';

/**
 * Check if a file on disk starts with the HDF5 magic signature.
 * Only reads the first 8 bytes — cheap even for huge mesh files.
 */
export async function isHdf5File(fsPath: string): Promise<boolean> {
  let handle: fs.promises.FileHandle | undefined;
  try {
    handle = await fs.promises.open(fsPath, 'r');
    const buffer = Buffer.alloc(HDF5_MAGIC.length);
    const { bytesRead } = await handle.read(buffer, 0, HDF5_MAGIC.length, 0);
    return bytesRead === HDF5_MAGIC.length && buffer.equals(HDF5_MAGIC);
  } catch {
    return false;
  } finally {
    await handle?.close();
  }
}

/**
 * Check if the given extension is already in `vs-code-aster.medFileExtensions`
 * (case-insensitive). Exported so `extension.ts` can use the same source of
 * truth when deciding whether to route a tab to the mesh viewer.
 */
export function isExtensionConfigured(ext: string): boolean {
  const config = vscode.workspace.getConfiguration('vs-code-aster');
  const current = config.get<string[]>('medFileExtensions', ['.med', '.mmed', '.rmed']);
  const normalized = ext.toLowerCase();
  return current.some((e) => e.toLowerCase() === normalized);
}

/**
 * Append an extension to `vs-code-aster.medFileExtensions` (globally).
 * No-op if already present.
 */
async function addExtensionToConfig(ext: string): Promise<void> {
  if (isExtensionConfigured(ext)) {
    return;
  }
  const config = vscode.workspace.getConfiguration('vs-code-aster');
  const current = config.get<string[]>('medFileExtensions', ['.med', '.mmed', '.rmed']);
  await config.update(
    'medFileExtensions',
    [...current, ext.toLowerCase()],
    vscode.ConfigurationTarget.Global
  );
}

/**
 * Close any text-editor tabs currently showing the given file URI. Called
 * before opening the custom editor so we don't end up with two tabs for the
 * same file (the stale binary-warning text tab plus the new viewer tab).
 */
async function closeTextTabsForUri(uri: vscode.Uri): Promise<void> {
  const targetPath = uri.fsPath;
  const tabsToClose: vscode.Tab[] = [];
  for (const group of vscode.window.tabGroups.all) {
    for (const tab of group.tabs) {
      if (tab.input instanceof vscode.TabInputText && tab.input.uri.fsPath === targetPath) {
        tabsToClose.push(tab);
      }
    }
  }
  if (tabsToClose.length > 0) {
    await vscode.window.tabGroups.close(tabsToClose);
  }
}

/**
 * Add the given URI's extension (if any) to the MED list, then reopen the
 * file in the mesh viewer. Used by both the command and the auto-detect
 * prompt's accept path.
 */
export async function openAsMedMesh(uri: vscode.Uri): Promise<void> {
  const ext = path.extname(uri.fsPath).toLowerCase();
  if (!ext) {
    vscode.window.showWarningMessage('File has no extension to add to the MED list.');
    return;
  }
  await addExtensionToConfig(ext);
  await closeTextTabsForUri(uri);
  await vscode.commands.executeCommand('vscode.openWith', uri, MedEditorProvider.viewType);
}

/**
 * Show an info notification offering to add the file's extension to the MED
 * list and reopen it in the viewer. Persistent "Don't ask" is stored per
 * extension in globalState.
 */
async function promptAddMedExtension(
  uri: vscode.Uri,
  context: vscode.ExtensionContext
): Promise<void> {
  const ext = path.extname(uri.fsPath).toLowerCase();
  if (!ext || STATIC_MED_EXTS.has(ext) || isExtensionConfigured(ext)) {
    return;
  }

  const declined = context.globalState.get<string[]>(DECLINED_EXTS_KEY, []);
  if (declined.includes(ext)) {
    return;
  }

  const addLabel = `Add ${ext} and open`;
  const notNow = 'Not now';
  const never = `Don't ask for ${ext}`;
  const choice = await vscode.window.showInformationMessage(
    `${path.basename(uri.fsPath)} looks like a MED mesh file. Add ${ext} to the MED extensions list?`,
    addLabel,
    notNow,
    never
  );

  if (choice === addLabel) {
    await openAsMedMesh(uri);
  } else if (choice === never) {
    await context.globalState.update(DECLINED_EXTS_KEY, [...declined, ext]);
  }
}

/**
 * Context key controlling the visibility of the "Open as MED mesh" button in
 * the editor title bar. Set to `true` when the active tab shows a file whose
 * first bytes match the HDF5 magic and whose extension isn't already
 * registered for MED.
 */
const CONTEXT_KEY = 'vs-code-aster.canConvertActiveToMed';

/** Extract a file URI from a Tab's input, if the tab points at a local file. */
function getTabFileUri(tab: vscode.Tab): vscode.Uri | undefined {
  const input: unknown = tab.input;
  if (
    input instanceof vscode.TabInputText ||
    input instanceof vscode.TabInputCustom ||
    input instanceof vscode.TabInputNotebook
  ) {
    const uri = (input as { uri: vscode.Uri }).uri;
    return uri.scheme === 'file' ? uri : undefined;
  }
  return undefined;
}

/**
 * Register listeners that peek at files as their tabs open and update the
 * title-bar context key. Using the tabs API (instead of `onDidChangeActive-
 * TextEditor`) is necessary because VS Code's "binary file" banner opens a
 * tab without creating an active text editor — we must react to the tab
 * event itself, or the auto-detect prompt never fires until the user
 * manually clicks "Open anyway".
 */
export function activateMedAutoDetect(context: vscode.ExtensionContext): void {
  const promptedPaths = new Set<string>();

  /** Check a file URI against the HDF5 magic bytes and prompt if unregistered. */
  const checkUriForPrompt = async (uri: vscode.Uri): Promise<boolean> => {
    const ext = path.extname(uri.fsPath).toLowerCase();
    if (!ext || STATIC_MED_EXTS.has(ext) || isExtensionConfigured(ext)) {
      return false;
    }
    if (!(await isHdf5File(uri.fsPath))) {
      return false;
    }
    if (!promptedPaths.has(uri.fsPath)) {
      promptedPaths.add(uri.fsPath);
      await promptAddMedExtension(uri, context);
    }
    return true;
  };

  /** Update the editor/title context key based on the currently active tab. */
  const refreshContextForActiveTab = async (): Promise<void> => {
    const activeTab = vscode.window.tabGroups.activeTabGroup?.activeTab;
    let canOffer = false;
    if (activeTab) {
      const uri = getTabFileUri(activeTab);
      if (uri) {
        const ext = path.extname(uri.fsPath).toLowerCase();
        if (ext && !STATIC_MED_EXTS.has(ext) && !isExtensionConfigured(ext)) {
          canOffer = await isHdf5File(uri.fsPath);
        }
      }
    }
    await vscode.commands.executeCommand('setContext', CONTEXT_KEY, canOffer);
  };

  context.subscriptions.push(
    vscode.window.tabGroups.onDidChangeTabs((event) => {
      for (const tab of event.opened) {
        const uri = getTabFileUri(tab);
        if (uri) {
          void checkUriForPrompt(uri);
        }
      }
      void refreshContextForActiveTab();
    })
  );

  // Prime state for whatever tab is already active at activation time.
  const activeTab = vscode.window.tabGroups.activeTabGroup?.activeTab;
  if (activeTab) {
    const uri = getTabFileUri(activeTab);
    if (uri) {
      void checkUriForPrompt(uri);
    }
  }
  void refreshContextForActiveTab();
}
