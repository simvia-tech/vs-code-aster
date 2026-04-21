import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkPoints from '@kitware/vtk.js/Common/Core/Points';
import vtkCellArray from '@kitware/vtk.js/Common/Core/CellArray';
import { GlobalSettings } from '../../settings/GlobalSettings';
import { VtkApp } from '../../core/VtkApp';

export class NodeActorCreator {
  private vertices: { x: number; y: number; z: number }[];
  private nodes: number[];
  private nodeIndexToGroup: number[];

  constructor(
    vertices: { x: number; y: number; z: number }[],
    nodes: number[],
    nodeIndexToGroup: number[]
  ) {
    this.vertices = vertices;
    this.nodes = nodes;
    this.nodeIndexToGroup = nodeIndexToGroup;
  }

  create(groupId: number): { actor: any; colorIndex: number } {
    const polyData = this.prepare(groupId);

    const mapper = vtkMapper.newInstance();
    mapper.setInputData(polyData);

    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);

    const colorIndex = this.setProperty(actor);
    VtkApp.Instance.getRenderer().addActor(actor);

    return { actor, colorIndex };
  }

  private prepare(groupId: number): any {
    const pd = vtkPolyData.newInstance();

    const nodeIndices = this.nodeIndexToGroup
      .map((g, idx) => (g === groupId ? idx : -1))
      .filter((idx) => idx !== -1);

    if (nodeIndices.length > 0) {
      const pts = vtkPoints.newInstance();
      const data: number[] = [];

      for (const idx of nodeIndices) {
        const v = this.vertices[this.nodes[idx]];
        if (v) {
          data.push(v.x, v.y, v.z);
        }
      }

      pts.setData(Float32Array.from(data), 3);
      pd.setPoints(pts);

      const numPoints = data.length / 3;
      const verts = vtkCellArray.newInstance();
      const vertData: number[] = [];

      for (let i = 0; i < numPoints; i++) {
        vertData.push(1, i);
      }

      verts.setData(Uint32Array.from(vertData));
      pd.setVerts(verts);
    }

    return pd;
  }

  private setProperty(actor: any): number {
    const prop = actor.getProperty();
    const colorIndex = GlobalSettings.Instance.grpIndex;
    prop.setRepresentation(0);
    prop.setOpacity(1);
    actor.setVisibility(false);
    prop.setColor(GlobalSettings.Instance.getColorForGroup());
    return colorIndex;
  }
}
