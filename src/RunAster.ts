import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';
import { parseRunOutput } from './OutputParser';

const execAsync = promisify(exec);

const LOG_FILENAME = '.vscode-aster-run.log';

export class RunAster {
  private static diagnosticCollection: vscode.DiagnosticCollection | undefined;
  private static logWatcher: vscode.FileSystemWatcher | undefined;

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

    // Parse .export to find all `F comm` entries so we can map traceback
    // paths (which reference `<basename>.changed.py` in a temp dir) back to
    // the user's original files.
    const commFiles = new Map<string, vscode.Uri>();
    try {
      const exportContent = fs.readFileSync(filePath, 'utf-8');
      for (const line of exportContent.split('\n')) {
        const parts = line.trim().split(/\s+/);
        if (parts[0] === 'F' && parts[1] === 'comm' && parts[2]) {
          let commPath = parts[2];
          if (!path.isAbsolute(commPath)) {
            commPath = path.join(fileDir, commPath);
          }
          commFiles.set(path.basename(commPath), vscode.Uri.file(commPath));
        }
      }
    } catch (error) {
      console.error('Failed to parse .export file:', error);
    }

    // Clear previous diagnostics and dispose old watcher
    if (RunAster.diagnosticCollection) {
      RunAster.diagnosticCollection.clear();
    }
    if (RunAster.logWatcher) {
      RunAster.logWatcher.dispose();
      RunAster.logWatcher = undefined;
    }

    // Capture all stdout/stderr via `tee` to a known log file so we can
    // parse the full run output regardless of whether `F mess` is set in
    // the `.export`. The user still sees live output in the terminal.
    const logPath = path.join(fileDir, LOG_FILENAME);
    try {
      if (fs.existsSync(logPath)) {
        fs.unlinkSync(logPath);
      }
    } catch (error) {
      console.error('Failed to remove old log file:', error);
    }

    const cmd = `${alias} ${fileName} 2>&1 | tee "${logPath}"`;

    let simulationTerminal = vscode.window.terminals.find((t) => t.name === 'code-aster runner');
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

    // Set up file watcher for the log file
    if (RunAster.diagnosticCollection) {
      const exportUri = editor.document.uri;
      const updateDiagnostics = () => {
        try {
          const logContent = fs.readFileSync(logPath, 'utf-8');
          const diagnosticsMap = parseRunOutput(logContent, exportUri, commFiles);

          RunAster.diagnosticCollection!.clear();
          for (const [uriKey, diags] of diagnosticsMap) {
            const uri = vscode.Uri.parse(uriKey);
            RunAster.diagnosticCollection!.set(uri, diags);
          }
        } catch (error) {
          console.error('Failed to parse run output:', error);
        }
      };

      RunAster.logWatcher = vscode.workspace.createFileSystemWatcher(logPath);
      RunAster.logWatcher.onDidCreate(updateDiagnostics);
      RunAster.logWatcher.onDidChange(updateDiagnostics);
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
