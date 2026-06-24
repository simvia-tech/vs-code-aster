import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';

export interface MeshGroups {
  volumes: string[];
  surfaces: string[];
  edges: string[];
  nodes: string[];
}

export interface MeshGroupsResult {
  version: number;
  meshName: string;
  meshDimension: number;
  groups: MeshGroups;
}

const EXPECTED_MESH_GROUPS_VERSION = 1;

/**
 * Extracts the JSON payload from mesh_groups.py stdout. The script prints the
 * payload as a single JSON line, but some Python environments inject extra
 * lines onto stdout (e.g. IDE REPL banners), so we scan from the last line for
 * the first one that parses to a versioned object.
 */
export function parseMeshGroupsStdout(stdout: string): MeshGroupsResult | null {
  const lines = stdout
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l.startsWith('{'));
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const obj = JSON.parse(lines[i]) as MeshGroupsResult;
      if (obj && typeof obj === 'object' && 'version' in obj && 'groups' in obj) {
        return obj;
      }
    } catch {
      // not this line; keep scanning
    }
  }
  return null;
}

/**
 * Runs python/mesh_groups.py against a .med file and returns the parsed group
 * structure. Mirrors the subprocess pattern in VisuManager.generateObjFromMed
 * (same pythonExecutablePath config, cwd, ENOENT / exit-code handling) but
 * resolves with JSON parsed from stdout instead of writing a file.
 */
export function extractMeshGroups(medFilePath: string): Promise<MeshGroupsResult> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, '..', 'python', 'mesh_groups.py');
    const config = vscode.workspace.getConfiguration('vs-code-aster');
    const pythonExecutablePath = config.get<string>('pythonExecutablePath', 'python3');

    const proc = spawn(pythonExecutablePath, [scriptPath, '-i', medFilePath], {
      cwd: path.dirname(medFilePath),
    });

    let stdout = '';
    let stderr = '';
    let settled = false;

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('error', (err: NodeJS.ErrnoException) => {
      if (settled) {
        return;
      }
      settled = true;
      if (err.code === 'ENOENT') {
        reject(
          new Error(
            `Python executable not found: "${pythonExecutablePath}". ` +
              `Please update the "vs-code-aster.pythonExecutablePath" setting.`
          )
        );
      } else {
        reject(new Error(`Failed to read mesh groups: ${err.message}`));
      }
    });

    proc.on('close', (code) => {
      if (settled) {
        return;
      }
      settled = true;
      if (code !== 0) {
        reject(new Error(`mesh_groups.py exited with code ${code}. ${stderr}`));
        return;
      }
      const parsed = parseMeshGroupsStdout(stdout);
      if (!parsed) {
        reject(new Error(`Could not parse mesh_groups.py output:\n${stdout}\n${stderr}`));
        return;
      }
      if (parsed.version !== EXPECTED_MESH_GROUPS_VERSION) {
        reject(
          new Error(
            `mesh_groups.py returned version ${parsed.version}, expected ${EXPECTED_MESH_GROUPS_VERSION}.`
          )
        );
        return;
      }
      resolve(parsed);
    });
  });
}

/**
 * Flattens all group kinds into a single deduplicated, sorted list — used when
 * we just need any group name regardless of topology.
 */
export function allGroupNames(groups: MeshGroups): string[] {
  return [
    ...new Set([...groups.volumes, ...groups.surfaces, ...groups.edges, ...groups.nodes]),
  ].sort();
}
