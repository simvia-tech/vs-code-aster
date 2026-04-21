import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkPoints from '@kitware/vtk.js/Common/Core/Points';
import vtkCellArray from '@kitware/vtk.js/Common/Core/CellArray';
import { GlobalSettings } from '../../settings/GlobalSettings';
import { VtkApp } from '../../core/VtkApp';

export class EdgeActorCreator {
  private vertices: { x: number; y: number; z: number }[];
  private edges: number[][];
  private edgeIndexToGroup: number[];

  constructor(
    vertices: { x: number; y: number; z: number }[],
    edges: number[][],
    edgeIndexToGroup: number[]
  ) {
    this.vertices = vertices;
    this.edges = edges;
    this.edgeIndexToGroup = edgeIndexToGroup;
  }

  create(groupId: number): { actor: any; colorIndex: number; cellCount: number } {
    const { polyData, cellCount } = this.prepare(groupId);

    const mapper = vtkMapper.newInstance();
    mapper.setInputData(polyData);
    EdgeActorCreator.applyDepthOffset(mapper, GlobalSettings.Instance.edgeGroupDepthOffset);

    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);

    const colorIndex = this.setProperty(actor);
    VtkApp.Instance.getRenderer().addActor(actor);

    return { actor, colorIndex, cellCount };
  }

  static applyDepthOffset(mapper: any, enabled: boolean): void {
    if (enabled) {
      mapper.setResolveCoincidentTopologyToPolygonOffset();
      mapper.setRelativeCoincidentTopologyLineOffsetParameters(-2, -2);
    } else {
      mapper.setResolveCoincidentTopologyToOff();
      mapper.setRelativeCoincidentTopologyLineOffsetParameters(0, 0);
    }
  }

  private prepare(groupId: number): { polyData: any; cellCount: number } {
    const pd = vtkPolyData.newInstance();

    const pts = vtkPoints.newInstance();
    const coords = new Float32Array(this.vertices.length * 3);
    this.vertices.forEach((v, i) => {
      coords[3 * i] = v.x;
      coords[3 * i + 1] = v.y;
      coords[3 * i + 2] = v.z;
    });
    pts.setData(coords, 3);
    pd.setPoints(pts);

    const edgeIndices = this.edgeIndexToGroup
      .map((g, idx) => (g === groupId ? idx : -1))
      .filter((idx) => idx !== -1);

    const cellCount = edgeIndices.length;
    if (cellCount > 0) {
      const lineArray = vtkCellArray.newInstance({
        values: Uint32Array.from(
          edgeIndices.flatMap((i) => {
            const e = this.edges[i];
            return [e.length, ...e];
          })
        ),
      });
      pd.setLines(lineArray);
    }

    return { polyData: pd, cellCount };
  }

  private setProperty(actor: any): number {
    const prop = actor.getProperty();
    const colorIndex = GlobalSettings.Instance.grpIndex;
    prop.setColor(GlobalSettings.Instance.getColorForGroup());
    prop.setLineWidth(GlobalSettings.Instance.edgeGroupThickness);
    prop.setLighting(false);
    actor.setVisibility(false);
    return colorIndex;
  }
}
