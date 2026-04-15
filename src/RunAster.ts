import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';
import { parseMessFile } from './MessFileParser';

const execAsync = promisify(exec);

export class RunAster {
  private static diagnosticCollection: vscode.DiagnosticCollection | undefined;
  private static messWatcher: vscode.FileSystemWatcher | undefined;

  /**
   * Initialize the diagnostic collection (called from extension.ts)
   */
  public static init(collection: vscode.DiagnosticCollection) {
    RunAster.diagnosticCollection = collection;
  }

  /**
   * Runs code_aster on the selected .export file in the workspace.
   */
  public static async runCodeAster() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage(`No active file found`);
      return;
    }

    const filePath = editor.document.uri.fsPath;
    const fileName = path.basename(filePath);
    const fileDir = path.dirname(filePath);

    if (!fileName.toLowerCase().includes('.export')) {
      vscode.window.showErrorMessage(`The active file is not an .export file`);
      return;
    }

    const config = vscode.workspace.getConfiguration('vs-code-aster');
    const alias = config.get<string>('aliasForRun', 'cave run');

    // TO DO : find a way to check alias that is compatible everywhere
    // const aliasIsValid = await RunAster.checkAlias(alias);
    // if (!aliasIsValid) {
    //     return;
    // }

    // Parse .export file to find mess and comm file paths
    let messPath: string | undefined;
    let commPath: string | undefined;
    try {
      const exportContent = fs.readFileSync(filePath, 'utf-8');
      for (const line of exportContent.split('\n')) {
        const parts = line.trim().split(/\s+/);
        if (parts[0] === 'F' && parts[1] === 'mess') {
          messPath = parts[2];
        }
        if (parts[0] === 'F' && parts[1] === 'comm') {
          commPath = parts[2];
        }
      }
      // Resolve relative paths against the export file directory
      if (messPath && !path.isAbsolute(messPath)) {
        messPath = path.join(fileDir, messPath);
      }
      if (commPath && !path.isAbsolute(commPath)) {
        commPath = path.join(fileDir, commPath);
      }
    } catch (error) {
      console.error('Failed to parse .export file:', error);
    }

    // Clear previous diagnostics and dispose old watcher
    if (RunAster.diagnosticCollection) {
      RunAster.diagnosticCollection.clear();
    }
    if (RunAster.messWatcher) {
      RunAster.messWatcher.dispose();
      RunAster.messWatcher = undefined;
    }

    // Find existing terminal or create a new one
    let simulationTerminal = vscode.window.terminals.find((t) => t.name === 'code-aster runner');

    const cmd = `${alias} ${fileName}`;

    if (simulationTerminal) {
      simulationTerminal.show();
      simulationTerminal.sendText(`cd "${fileDir}" && ${cmd}`);
    } else {
      simulationTerminal = vscode.window.createTerminal({
        name: 'code-aster runner',
        cwd: fileDir,
      });
      simulationTerminal.show();
      simulationTerminal.sendText(cmd);
    }

    // Set up file watcher for .mess output file
    if (messPath && RunAster.diagnosticCollection) {
      const updateDiagnostics = () => {
        try {
          const messContent = fs.readFileSync(messPath!, 'utf-8');
          const commUri = commPath ? vscode.Uri.file(commPath) : undefined;
          const diagnosticsMap = parseMessFile(messContent, editor.document.uri, commUri);

          // Clear and repopulate diagnostics
          RunAster.diagnosticCollection!.clear();
          for (const [uriKey, diags] of diagnosticsMap) {
            const uri = vscode.Uri.parse(uriKey);
            RunAster.diagnosticCollection!.set(uri, diags);
          }
        } catch (error) {
          console.error('Failed to parse .mess file:', error);
        }
      };

      RunAster.messWatcher = vscode.workspace.createFileSystemWatcher(messPath);
      RunAster.messWatcher.onDidCreate(updateDiagnostics);
      RunAster.messWatcher.onDidChange(updateDiagnostics);
    }
  }

  /**
   * Verify the user's alias and return true if it exists on the system
   * */
  private static async checkAlias(alias: string): Promise<boolean> {
    const firstWord = alias.split(' ')[0];

    try {
      const { stdout } = await execAsync(`which ${firstWord}`);
      if (stdout) {
        return true;
      }
    } catch {}

    if (firstWord === 'cave') {
      const selection = await vscode.window.showWarningMessage(
        `"Cave" (default tool) not found. You can download it or set a personal alias.`,
        'Download Cave',
        'Edit Alias'
      );
      if (selection === 'Download Cave') {
        vscode.env.openExternal(vscode.Uri.parse('https://github.com/simvia-tech/cave'));
      } else if (selection === 'Edit Alias') {
        vscode.commands.executeCommand(
          'workbench.action.openSettings',
          'vs-code-aster.aliasForRun'
        );
      }
    } else {
      const selection = await vscode.window.showWarningMessage(
        `The command "${firstWord}" from your alias "${alias}" does not exist on your system.`,
        'Edit Alias'
      );
      if (selection === 'Edit Alias') {
        vscode.commands.executeCommand(
          'workbench.action.openSettings',
          'vs-code-aster.aliasForRun'
        );
      }
    }

    return false;
  }
}
