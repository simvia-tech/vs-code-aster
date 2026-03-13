import { GlobalSettings } from '../settings/GlobalSettings';
import { ObjLoader } from './ObjLoader';
import { FaceActorCreator } from './create/FaceActorCreator';
import { NodeActorCreator } from './create/NodeActorCreator';
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

  do(): void {
    const result = ObjLoader.loadFiles(this.fileContexts, this.fileNames);
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
      faceGroups,
      nodeGroups,
      groupHierarchy,
    } = result;

    const faceActorCreator = new FaceActorCreator(vertices, cells, cellIndexToGroup);
    const nodeActorCreator = new NodeActorCreator(vertices, nodes, nodeIndexToGroup);

    for (const fileGroup in groupHierarchy) {
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
        true,
        null,
        null,
        fileColorIndex,
        fileIsObj,
        fileCellCount
      );
      this.groups[fileGroup] = groupInstance;

      const size = this.computeSize(actor);

      for (const faceGroup of groupHierarchy[fileGroup].faces) {
        const faceGroupId = faceGroups.indexOf(`${fileGroup}::${faceGroup}`);
        const {
          actor: faceActor,
          colorIndex: faceColorIndex,
          isObjectActor: faceIsObj,
          cellCount: faceCellCount,
        } = faceActorCreator.create(faceGroup, faceGroupId);
        const subGroup = new Group(
          faceActor,
          faceGroup,
          true,
          fileGroup,
          size,
          faceColorIndex,
          faceIsObj,
          faceCellCount
        );
        this.groups[`${fileGroup}::${faceGroup}`] = subGroup;
      }

      for (const nodeGroup of groupHierarchy[fileGroup].nodes) {
        const nodeGroupId = nodeGroups.indexOf(`${fileGroup}::${nodeGroup}`);
        const { actor: nodeActor, colorIndex: nodeColorIndex } =
          nodeActorCreator.create(nodeGroupId);
        const subGroup = new Group(
          nodeActor,
          nodeGroup,
          false,
          fileGroup,
          size,
          nodeColorIndex,
          false
        );
        this.groups[`${fileGroup}::${nodeGroup}`] = subGroup;
      }
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
