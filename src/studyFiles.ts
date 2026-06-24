import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { StudySpec } from './scenario/spec';
import { generateComm } from './scenario/generateComm';
import { generateExport } from './scenario/generateExport';
import { extractMeshGroups, MeshGroups } from './MeshGroups';

const EMPTY_GROUPS: MeshGroups = { volumes: [], surfaces: [], edges: [], nodes: [] };

/** Prompt for the MED mesh to base the study on (defaults to the active .med). */
export async function pickMeshFile(): Promise<string | undefined> {
  const active = vscode.window.activeTextEditor?.document.uri;
  const activeIsMed = active && /\.(med|mmed|rmed)$/i.test(active.fsPath);
  const defaultUri = activeIsMed ? active : vscode.workspace.workspaceFolders?.[0]?.uri;

  const picked = await vscode.window.showOpenDialog({
    canSelectMany: false,
    openLabel: 'Use this mesh',
    title: 'Select the MED mesh for the study',
    defaultUri,
    filters: { 'MED mesh': ['med', 'mmed', 'rmed'] },
  });
  return picked?.[0]?.fsPath;
}

export interface GroupsResult {
  groups: MeshGroups;
  /** False when the groups could not be read (no Python / medcoupling / bad mesh). */
  available: boolean;
}

/** Read the mesh groups via mesh_groups.py, with progress and a graceful fallback. */
export async function readGroups(medPath: string): Promise<GroupsResult> {
  try {
    const result = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: 'Reading mesh groups…' },
      () => extractMeshGroups(medPath)
    );
    return { groups: result.groups, available: true };
  } catch (err) {
    vscode.window.showWarningMessage(
      `Could not read mesh groups (${err instanceof Error ? err.message : String(err)}). ` +
        'You can type group names manually.'
    );
    return { groups: { ...EMPTY_GROUPS }, available: false };
  }
}

/**
 * Write the generated study into a self-contained `<baseName>/` folder beside
 * the mesh: `<baseName>.comm`, `<baseName>.export`, and a copy of the mesh.
 * Opens the generated `.comm` afterwards. Reused by the wizard and the webview.
 */
export async function writeStudy(spec: StudySpec, medPath: string): Promise<void> {
  const meshDir = path.dirname(medPath);
  const outputDir = path.join(meshDir, spec.baseName);

  if (fs.existsSync(outputDir)) {
    const choice = await vscode.window.showWarningMessage(
      `Folder "${spec.baseName}" already exists. Overwrite its study files?`,
      { modal: true },
      'Overwrite'
    );
    if (choice !== 'Overwrite') {
      return;
    }
  }
  fs.mkdirSync(outputDir, { recursive: true });

  const commPath = path.join(outputDir, `${spec.baseName}.comm`);
  const exportPath = path.join(outputDir, `${spec.baseName}.export`);
  const meshDest = path.join(outputDir, spec.meshFileName);

  fs.writeFileSync(commPath, generateComm(spec), 'utf8');
  fs.writeFileSync(exportPath, generateExport(spec), 'utf8');
  try {
    if (path.resolve(meshDest) !== path.resolve(medPath)) {
      fs.copyFileSync(medPath, meshDest);
    }
  } catch (err) {
    vscode.window.showWarningMessage(
      `Study generated, but the mesh could not be copied into the folder: ${
        err instanceof Error ? err.message : String(err)
      }`
    );
  }

  await vscode.window.showTextDocument(vscode.Uri.file(commPath));
  vscode.window.showInformationMessage(`Generated study "${spec.baseName}".`);
}
