import * as vscode from 'vscode';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class RunAster {
   
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

        const simulationTerminal = vscode.window.createTerminal({ name: "code-aster runner", cwd: fileDir });
        
        const cmd = `${alias} ${fileName}`;
        simulationTerminal.show();
        simulationTerminal.sendText(cmd);
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
        } catch {
        }

        if (firstWord === 'cave') {
            const selection = await vscode.window.showWarningMessage(
                `"Cave" (default tool) not found. You can download it or set a personal alias.`,
                "Download Cave",
                "Edit Alias"
            );
            if (selection === "Download Cave") {
                vscode.env.openExternal(vscode.Uri.parse("https://github.com/simvia-tech/cave"));
            } else if (selection === "Edit Alias") {
                vscode.commands.executeCommand('workbench.action.openSettings', 'vs-code-aster.aliasForRun');
            }
        } else {
            const selection = await vscode.window.showWarningMessage(
                `The command "${firstWord}" from your alias "${alias}" does not exist on your system.`,
                "Edit Alias"
            );
            if (selection === "Edit Alias") {
                vscode.commands.executeCommand('workbench.action.openSettings', 'vs-code-aster.aliasForRun');
            }
        }

        return false;
    }
}
