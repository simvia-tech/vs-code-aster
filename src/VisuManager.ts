import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import { spawn } from "child_process";
import { sendTelemetry, TelemetryType } from "./telemetry";
import { WebviewVisu } from "./WebviewVisu";
import { TextDecoder } from "util";

/**
 * List of supported Code Aster command file extensions.
 */
export const SUPPORTED_COMM_EXTENSIONS = [
  ".comm",
  ".com",
  ".com0",
  ".com1",
  ".com2",
  ".com3",
  ".com4",
  ".com5",
  ".com6",
  ".com7",
  ".com8",
  ".com9",
];

/**
 * Checks if a file path has a valid comm file extension.
 * Supports all configured comm file extensions.
 * @param filePath Path to the file to check
 * @returns True if the file has a valid comm extension, false otherwise
 */
function isCommFile(filePath: string): boolean {
  const config = vscode.workspace.getConfiguration("vs-code-aster");
  const configuredExtensions = config.get<string[]>(
    "commFileExtensions",
    SUPPORTED_COMM_EXTENSIONS,
  );
  const ext = path.extname(filePath).toLowerCase();
  return configuredExtensions.some(
    (extConfig) => extConfig.toLowerCase() === ext,
  );
}

/**
 * Represents an open Webview associated with a .comm file.
 */
interface WebviewEntry {
  /** URI of the .comm file */
  commUri: vscode.Uri;
  /** URIs of the .obj files associated with the .comm */
  objUris: vscode.Uri[];
  /** The WebviewVisu instance controlling the webview */
  visu: WebviewVisu;
}

/**
 * Manages all "Mesh Viewer" Webviews in the extension.
 * Handles creation, display, coloring, and highlighting of mesh groups.
 */
export class VisuManager {
  private static _instance: VisuManager;
  private views: Map<string, WebviewEntry> = new Map();

  private constructor() {}

  /**
   * Gets the singleton instance of VisuManager.
   */
  public static get instance(): VisuManager {
    if (!VisuManager._instance) {
      VisuManager._instance = new VisuManager();
      VisuManager._instance.listenCommFiles();
    }
    return VisuManager._instance;
  }

  /**
   * Creates or shows a mesh viewer webview for the active comm file.
   */
  public async createOrShowMeshViewer() {
    // We retrieve the concerned comm file
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
      vscode.window.showWarningMessage("No active editor.");
      return;
    }
    const filePath = editor.document.uri.fsPath;
    if (!isCommFile(filePath)) {
      vscode.window.showWarningMessage(
        "The active file is not a Code Aster command file.",
      );
      return;
    }

    const commUri = editor.document.uri;
    const key = commUri.fsPath;

    if (this.views.has(key)) {
      const entry = this.views.get(key)!;
      entry.visu.panel.reveal(vscode.ViewColumn.Beside);
      return;
    }
    const medFiles = findMedFiles(commUri.fsPath);

    let objUris: vscode.Uri[] = [];

    if (medFiles.length === 0) {
      return;
    }

    objUris = await getObjFiles(medFiles);

    if (objUris.length === 0) {
      return;
    }

    const fileContexts = await readObjFilesContent(objUris);

    const testDir = path.resolve(__dirname, "..");

    const visu = new WebviewVisu(
      "meshViewer",
      testDir,
      "resources/visu_vtk/index.html",
      fileContexts,
      objUris.map((uri) => path.basename(uri.fsPath)),
    );

    this.views.set(key, { commUri, objUris, visu });

    // Send telemetry once per opening of this .comm (non-blocking).
    // This will not run when simply revealing an existing viewer.
    void sendTelemetry(TelemetryType.VIEWER_OPENED);

    visu.panel.onDidDispose(() => {
      this.views.delete(key);
    });
  }

  public getViewer(commUri: vscode.Uri): WebviewEntry | undefined {
    return this.views.get(commUri.fsPath);
  }

  public listenCommFiles() {
    vscode.window.onDidChangeTextEditorSelection((event) => {
      const editor = event.textEditor;
      const filePath = editor.document.uri.fsPath;

      if (!isCommFile(filePath)) {
        return;
      }

      const commUri = editor.document.uri;
      const firstSelection = editor.selections.find((sel) => !sel.isEmpty);
      const selectedText = firstSelection
        ? editor.document.getText(firstSelection)
        : "";
      const entry = this.getViewer(commUri);
      if (!entry) {
        return;
      }
      entry.visu.showGroupsFromTextSelection(selectedText);
    });
  }
}

/**
 * Reads the contents of all .obj files and returns them as a string array.
 * @param objUris Array of vscode.Uri for .obj files
 */
export async function readObjFilesContent(
  objUris: vscode.Uri[],
): Promise<string[]> {
  const decoder = new TextDecoder("utf-8");
  const contexts: string[] = [];
  for (const uri of objUris) {
    try {
      const fileData = await vscode.workspace.fs.readFile(uri);
      contexts.push(decoder.decode(fileData));
    } catch (err) {
      vscode.window.showErrorMessage(`Error reading .obj file: ${uri.fsPath}`);
    }
  }
  return contexts;
}

/**
 * Finds the .*med files corresponding to a given .comm file by reading .export files in the same folder.
 * @param commFilePath Path to the .comm file
 * @returns Paths to the .*med files if found, [] otherwise
 */
export function findMedFiles(commFilePath: string): string[] {
  try {
    const dir = path.dirname(commFilePath);
    const commFileName = path.basename(commFilePath);
    const exportFiles = fs
      .readdirSync(dir)
      .filter((f) => f.endsWith(".export"));

    if (exportFiles.length === 0) {
      vscode.window.showErrorMessage(
        `No .export file found in directory: ${dir}`,
      );
      return [];
    }

    const foundMedFiles: string[] = [];

    for (const exportFile of exportFiles) {
      const exportPath = path.join(dir, exportFile);
      const content = fs.readFileSync(exportPath, "utf8");

      if (!content.includes(commFileName)) {
        continue;
      }

      const lines = content.split(/\r?\n/);
      for (const line of lines) {
        if (!/\bD\b/.test(line)) {
          continue;
        }

        const match = line.match(/([\w\-./\\]+\.[a-z]?med)\b/i);
        if (match) {
          const medFileName = path.basename(match[1]);
          const medPath = path.join(dir, medFileName);

          if (fs.existsSync(medPath)) {
            console.log(`[findMedFiles] found med file: ${medFileName}`);
            foundMedFiles.push(medPath);
          } else {
            vscode.window.showErrorMessage(
              `The file "${medFileName}" mentioned in "${exportFile}" does not exist in the current directory (${path.basename(
                dir,
              )}/).`,
            );
          }
        }
      }
    }

    if (foundMedFiles.length === 0) {
      vscode.window.showErrorMessage(
        `No .export file in "${path.basename(
          dir,
        )}/" references any entry .med file associated with ${commFileName}.`,
      );
    }

    return foundMedFiles;
  } catch (err) {
    vscode.window.showErrorMessage(
      `Error while searching for .med file: ${(err as Error).message}`,
    );
    return [];
  }
}

/**
 * Returns the .obj files associated with the given .mmed files. Creates a .visu_data folder if needed.
 * @param medFiles Array of .mmed file paths
 * @returns Array of URIs for found .obj files
 */
export async function getObjFiles(medFiles: string[]): Promise<vscode.Uri[]> {
  const objUris: vscode.Uri[] = [];
  for (const mmedFilePath of medFiles) {
    try {
      const mmedDir = path.dirname(mmedFilePath);
      const ext = path.extname(mmedFilePath);
      const mmedBase = path.basename(mmedFilePath, ext);
      const visuDataDir = path.join(mmedDir, ".visu_data");
      if (!fs.existsSync(visuDataDir)) {
        fs.mkdirSync(visuDataDir, { recursive: true });
        console.log(`[getObjFiles] Created directory: ${visuDataDir}`);
      }
      const objFilePath = path.join(visuDataDir, `${mmedBase}.obj`);
      if (fs.existsSync(objFilePath)) {
        const mmedStat = fs.statSync(mmedFilePath);
        const objStat = fs.statSync(objFilePath);
        if (objStat.mtime < mmedStat.mtime) {
          vscode.window.showInformationMessage(
            `.obj file is outdated and being regenerated: ${path.basename(
              objFilePath,
            )}`,
          );
          console.log(`[getObjFiles] .obj file is outdated: ${objFilePath}`);
          await generateObjFromMed(mmedFilePath, objFilePath);
        }
        console.log(`[getObjFiles] .obj file found: ${objFilePath}`);
        objUris.push(vscode.Uri.file(objFilePath));
      } else {
        console.log(`[getObjFiles] .obj file not found for ${mmedBase}.`);
        vscode.window.showInformationMessage(
          `Creating .obj file for: ${path.basename(mmedFilePath)}`,
        );
        await generateObjFromMed(mmedFilePath, objFilePath);
        if (fs.existsSync(objFilePath)) {
          objUris.push(vscode.Uri.file(objFilePath));
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);

      if (msg.includes("No module named 'medcoupling'")) {
        vscode.window.showErrorMessage(
          "Python module 'medcoupling' is not installed. " +
            "Please install it by running `pip install medcoupling` in your Python environment, then retry.",
        );
      } else {
        vscode.window.showErrorMessage(
          `Error while searching for .obj file: ${(err as Error).message}`,
        );
      }
    }
  }
  return objUris;
}

/**
 * Generates a .obj file from a .med file by calling the med2obj.py Python script.
 * @param medFilePath Path to the input .med file
 * @param objFilePath Path to the output .obj file
 */
async function generateObjFromMed(
  medFilePath: string,
  objFilePath: string,
): Promise<void> {
  return new Promise((resolve, reject) => {
    // Locate med2obj.py script - assumed to be in python/asterstudy/post or similar
    const scriptPath = path.join(__dirname, "..", "python", "med2obj.py");

    console.log(
      `[generateObjFromMed] Executing: python ${scriptPath} ${medFilePath} ${objFilePath}`,
    );

    const config = vscode.workspace.getConfiguration("vs-code-aster");
    const pythonExecutablePath = config.get<string>(
      "pythonExecutablePath",
      "python3",
    );

    const process = spawn(
      pythonExecutablePath,
      [scriptPath, "-i", medFilePath, "-o", objFilePath],
      {
        cwd: path.dirname(medFilePath),
      },
    );

    let stderr = "";

    process.stderr.on("data", (data) => {
      stderr += data.toString();
      console.log(`[generateObjFromMed] stderr: ${data}`);
    });

    process.on("error", (err) => {
      console.error(`[generateObjFromMed] Process error: ${err.message}`);
      reject(new Error(`Failed to generate .obj file: ${err.message}`));
    });

    process.on("close", (code) => {
      if (code === 0) {
        console.log(
          `[generateObjFromMed] Successfully generated: ${objFilePath}`,
        );
        resolve();
      } else {
        const errorMsg = `med2obj.py exited with code ${code}. ${stderr}`;
        console.error(`[generateObjFromMed] ${errorMsg}`);
        reject(new Error(errorMsg));
      }
    });
  });
}
