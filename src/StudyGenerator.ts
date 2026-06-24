import * as vscode from 'vscode';
import { pickMeshFile, readGroups } from './studyFiles';
import { StudyWebview } from './StudyWebview';

/**
 * Entry point for the "Generate study from scenario" command. Picks the mesh,
 * reads its groups, then opens the study webview (which collects the StudySpec,
 * previews the generated files, and writes them on submit).
 */
export class StudyGenerator {
  static async run(_context?: vscode.ExtensionContext): Promise<void> {
    try {
      const medPath = await pickMeshFile();
      if (!medPath) {
        return;
      }
      const { groups, available } = await readGroups(medPath);
      StudyWebview.show(medPath, groups, available);
    } catch (err) {
      vscode.window.showErrorMessage(
        `Generate study failed: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  }
}
