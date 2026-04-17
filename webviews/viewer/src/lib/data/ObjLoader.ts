import { Controller } from '../Controller';

export interface ObjLoaderResult {
  vertices: { x: number; y: number; z: number }[];
  cells: number[][];
  cellIndexToGroup: number[];
  nodes: number[];
  nodeIndexToGroup: number[];
  faceGroups: string[];
  nodeGroups: string[];
  groupHierarchy: Record<string, { faces: string[]; nodes: string[] }>;
}

const YIELD_EVERY_LINES = 5_000;

export class ObjLoader {
  static async loadFiles(
    fileContexts: string[],
    fileNames: string[],
    onProgress: (progress: number) => void,
    onMessage: (message: string) => void
  ): Promise<ObjLoaderResult> {
    const vertices: { x: number; y: number; z: number }[] = [];
    const cells: number[][] = [];
    const cellIndexToGroup: number[] = [];
    const nodes: number[] = [];
    const nodeIndexToGroup: number[] = [];
    const faceGroups: string[] = [];
    const nodeGroups: string[] = [];
    const groupHierarchy: Record<string, { faces: string[]; nodes: string[] }> = {};

    let nbVertices = 0;
    let groupId = -1;
    let nodeGroupId = -1;

    const yield_ = () => new Promise<void>((r) => setTimeout(r, 0));

    for (let i = 0; i < fileContexts.length; i++) {
      try {
        groupId++;
        const skinName = 'all_' + fileNames[i];

        groupHierarchy[skinName] = { faces: [], nodes: [] };
        faceGroups.push(skinName);
        nbVertices = vertices.length;

        onMessage(`Parsing ${fileNames[i]}...`);
        const lines = fileContexts[i].split('\n').map((l) => l.replace('\r', ''));
        const totalLines = lines.length;

        for (let lineIdx = 0; lineIdx < totalLines; lineIdx++) {
          if (lineIdx % YIELD_EVERY_LINES === 0 && lineIdx > 0) {
            const fileProgress = (i + lineIdx / totalLines) / fileContexts.length;
            onProgress(fileProgress * 0.9);
            await yield_();
          }

          const line = lines[lineIdx];
          if (line.startsWith('#')) {
            continue;
          }
          const ss = line.split(' ').filter((p) => p.length !== 0);
          if (ss.length === 0) {
            continue;
          }

          switch (ss[0]) {
            case 'v':
              vertices.push({
                x: Number.parseFloat(ss[1]),
                y: Number.parseFloat(ss[2]),
                z: Number.parseFloat(ss[3]),
              });
              break;

            case 'f': {
              const faceIndices = ss.slice(1).map((p) => Number.parseInt(p) - 1 + nbVertices);
              cells.push(faceIndices);
              cellIndexToGroup.push(groupId);
              break;
            }

            case 'g': {
              groupId++;
              const faceGroupName = ss[1] || `group${groupId}`;
              faceGroups.push(`${skinName}::${faceGroupName}::face`);
              groupHierarchy[skinName].faces.push(faceGroupName);
              break;
            }

            case 'ng': {
              nodeGroupId++;
              const nodeGroupName = ss[1] || `nodeGroup${nodeGroupId}`;
              nodeGroups.push(`${skinName}::${nodeGroupName}::node`);
              groupHierarchy[skinName].nodes.push(nodeGroupName);
              break;
            }

            case 'p': {
              const nodeIndex = parseInt(ss[1]);
              nodes.push(nodeIndex - 1 + nbVertices);
              nodeIndexToGroup.push(nodeGroupId);
              break;
            }
          }
        }

        onProgress(((i + 1) / fileContexts.length) * 0.9);
        await yield_();
      } catch (fileError: any) {
        Controller.Instance.getVSCodeAPI().postMessage({
          type: 'debugPanel',
          text: `ERROR: ${fileError.message}`,
        });
        throw fileError;
      }
    }

    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'debugPanel',
      text: `TOTAL: ${vertices.length} vertices, ${cells.length} cells, ${nodes.length} nodes`,
    });

    return {
      vertices,
      cells,
      cellIndexToGroup,
      nodes,
      nodeIndexToGroup,
      faceGroups,
      nodeGroups,
      groupHierarchy,
    };
  }
}
