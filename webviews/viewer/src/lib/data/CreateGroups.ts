import { GlobalSettings } from '../settings/GlobalSettings';
import { ObjLoader } from './ObjLoader';
import { FaceActorCreator } from './create/FaceActorCreator';
import { NodeActorCreator } from './create/NodeActorCreator';
import { EdgeActorCreator } from './create/EdgeActorCreator';
import { Group } from './Group';
import { Controller } from '../Controller';
import { VtkApp } from '../core/VtkApp';

export class CreateGroups {
  private fileContexts: string[];
  private fileNames: string[];
  groups: Record<string, Group> = {};

  constructor(fileContexts: string[], fileNames: string[]) {
    this.fileContexts = fileContexts;
    this.fileNames = fileNames;
  }

  async do(
    onProgress: (progress: number) => void,
    onMessage: (message: string) => void
  ): Promise<void> {
    const result = await ObjLoader.loadFiles(
      this.fileContexts,
      this.fileNames,
      onProgress,
      onMessage
    );
    const post = (text: string) => {
      Controller.Instance.getVSCodeAPI().postMessage({ type: 'debugPanel', text });
    };

    if (!result) {
      return;
    }

    const {
      vertices,
      cells,
      cellIndexToGroup,
      nodes,
      nodeIndexToGroup,
      edges,
      edgeIndexToGroup,
      faceGroups,
      nodeGroups,
      edgeGroups,
      groupHierarchy,
    } = result;

    const faceActorCreator = new FaceActorCreator(vertices, cells, cellIndexToGroup);
    const nodeActorCreator = new NodeActorCreator(vertices, nodes, nodeIndexToGroup);
    const edgeActorCreator = new EdgeActorCreator(vertices, edges, edgeIndexToGroup);

    const edgeKey = (a: number, b: number) => (a < b ? `${a}-${b}` : `${b}-${a}`);
    const faceEdgeSet = new Set<string>();
    for (const cell of cells) {
      for (let i = 0; i < cell.length; i++) {
        faceEdgeSet.add(edgeKey(cell[i], cell[(i + 1) % cell.length]));
      }
    }
    const standaloneByFile: Record<string, number[]> = {};
    for (let i = 0; i < edges.length; i++) {
      const e = edges[i];
      let isStandalone = false;
      for (let j = 0; j + 1 < e.length; j++) {
        if (!faceEdgeSet.has(edgeKey(e[j], e[j + 1]))) {
          isStandalone = true;
          break;
        }
      }
      if (!isStandalone) continue;
      const egId = edgeIndexToGroup[i];
      if (egId < 0) continue;
      const fileGroup = edgeGroups[egId]?.split('::')[0];
      if (!fileGroup) continue;
      (standaloneByFile[fileGroup] ||= []).push(i);
    }

    const groupKeys = Object.keys(groupHierarchy);
    const yield_ = () => new Promise<void>((r) => setTimeout(r, 0));

    onMessage('Building scene...');
    for (let gi = 0; gi < groupKeys.length; gi++) {
      const fileGroup = groupKeys[gi];
      const groupId = faceGroups.indexOf(fileGroup);

      const _oc = GlobalSettings.Instance.objectColors;
      const objColor = _oc[GlobalSettings.Instance.objIndex % _oc.length];
      (groupHierarchy[fileGroup] as any).color = objColor;

      const {
        actor,
        colorIndex: fileColorIndex,
        isObjectActor: fileIsObj,
        cellCount: fileCellCount,
      } = faceActorCreator.create(fileGroup, groupId, true);

      const groupInstance = new Group(
        actor,
        fileGroup,
        'face',
        null,
        null,
        fileColorIndex,
        fileIsObj,
        fileCellCount
      );
      this.groups[fileGroup] = groupInstance;

      const standaloneIdx = standaloneByFile[fileGroup];
      if (standaloneIdx && standaloneIdx.length > 0) {
        const result = edgeActorCreator.createStandalone(standaloneIdx, objColor);
        if (result) {
          groupInstance.standaloneEdgesActor = result.actor;
          groupInstance.standaloneEdgesContourActor = result.contourActor;
        }
      }

      const size = this.computeSize(actor);

      for (const volumeGroup of groupHierarchy[fileGroup].volumes) {
        const key = `${fileGroup}::${volumeGroup}::volume`;
        const volumeGroupId = faceGroups.indexOf(key);
        const {
          actor: volumeActor,
          colorIndex: volumeColorIndex,
          isObjectActor: volumeIsObj,
          cellCount: volumeCellCount,
        } = faceActorCreator.create(volumeGroup, volumeGroupId);
        const subGroup = new Group(
          volumeActor,
          volumeGroup,
          'volume',
          fileGroup,
          size,
          volumeColorIndex,
          volumeIsObj,
          volumeCellCount
        );
        this.groups[key] = subGroup;
      }

      for (const faceGroup of groupHierarchy[fileGroup].faces) {
        const faceGroupId = faceGroups.indexOf(`${fileGroup}::${faceGroup}::face`);
        const {
          actor: faceActor,
          colorIndex: faceColorIndex,
          isObjectActor: faceIsObj,
          cellCount: faceCellCount,
        } = faceActorCreator.create(faceGroup, faceGroupId);
        const subGroup = new Group(
          faceActor,
          faceGroup,
          'face',
          fileGroup,
          size,
          faceColorIndex,
          faceIsObj,
          faceCellCount
        );
        this.groups[`${fileGroup}::${faceGroup}::face`] = subGroup;
      }

      for (const edgeGroup of groupHierarchy[fileGroup].edges) {
        const edgeGroupId = edgeGroups.indexOf(`${fileGroup}::${edgeGroup}::edge`);
        const {
          actor: edgeActor,
          colorIndex: edgeColorIndex,
          cellCount: edgeCellCount,
        } = edgeActorCreator.create(edgeGroupId);
        const subGroup = new Group(
          edgeActor,
          edgeGroup,
          'edge',
          fileGroup,
          size,
          edgeColorIndex,
          false,
          edgeCellCount
        );
        this.groups[`${fileGroup}::${edgeGroup}::edge`] = subGroup;
      }

      for (const nodeGroup of groupHierarchy[fileGroup].nodes) {
        const nodeGroupId = nodeGroups.indexOf(`${fileGroup}::${nodeGroup}::node`);
        const { actor: nodeActor, colorIndex: nodeColorIndex } =
          nodeActorCreator.create(nodeGroupId);
        const subGroup = new Group(
          nodeActor,
          nodeGroup,
          'node',
          fileGroup,
          size,
          nodeColorIndex,
          false
        );
        this.groups[`${fileGroup}::${nodeGroup}::node`] = subGroup;
      }

      onProgress(0.9 + ((gi + 1) / groupKeys.length) * 0.1);
      await yield_();
    }

    VtkApp.Instance.getRenderer().resetCamera();
    VtkApp.Instance.getRenderWindow().render();
    post(`actors : ${Object.keys(this.groups).length}`);

    Controller.Instance.saveGroups(this.groups, groupHierarchy);
  }

  private computeSize(actor: any): number {
    const bounds = actor.getBounds();
    const dx = bounds[1] - bounds[0];
    const dy = bounds[3] - bounds[2];
    const dz = bounds[5] - bounds[4];
    const size = Math.sqrt(dx * dx + dy * dy + dz * dz);
    return Math.max(size, 1e-3);
  }
}
