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
      } = faceActorCreator.create(fileGroup, groupId);

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
