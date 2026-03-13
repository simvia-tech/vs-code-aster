import { GlobalSettings } from '../../settings/GlobalSettings';
import { VtkApp } from '../../core/VtkApp';

export class FaceActorCreator {
  private vertices: { x: number; y: number; z: number }[];
  private cells: number[][];
  private cellIndexToGroup: number[];

  constructor(
    vertices: { x: number; y: number; z: number }[],
    cells: number[][],
    cellIndexToGroup: number[],
  ) {
    this.vertices = vertices;
    this.cells = cells;
    this.cellIndexToGroup = cellIndexToGroup;
  }

  create(groupName: string, groupId: number): { actor: any; colorIndex: number; isObjectActor: boolean; cellCount: number } {
    const { polyData, cellCount } = this.prepare(groupId);

    const actor = vtk.Rendering.Core.vtkActor.newInstance();
    const mapper = vtk.Rendering.Core.vtkMapper.newInstance();

    mapper.setInputData(polyData);
    actor.setMapper(mapper);

    const { colorIndex, isObjectActor } = this.setProperty(actor, groupName, cellCount);
    VtkApp.Instance.getRenderer().addActor(actor);

    return { actor, colorIndex, isObjectActor, cellCount };
  }

  private prepare(groupId: number): { polyData: any; cellCount: number } {
    const pd = vtk.Common.DataModel.vtkPolyData.newInstance();

    const pts = vtk.Common.Core.vtkPoints.newInstance();
    const coords = new Float32Array(this.vertices.length * 3);
    this.vertices.forEach((v, i) => {
      coords[3 * i] = v.x;
      coords[3 * i + 1] = v.y;
      coords[3 * i + 2] = v.z;
    });
    pts.setData(coords, 3);
    pd.setPoints(pts);

    const cellIndices = this.cellIndexToGroup
      .map((g, idx) => (g === groupId ? idx : -1))
      .filter((idx) => idx !== -1);

    const cellCount = cellIndices.length;
    if (cellCount > 0) {
      const cellArray = vtk.Common.Core.vtkCellArray.newInstance({
        values: Uint32Array.from(
          cellIndices.flatMap((i) => {
            const c = this.cells[i];
            return [c.length, ...c];
          }),
        ),
      });
      pd.setPolys(cellArray);
    }

    return { polyData: pd, cellCount };
  }

  private setProperty(actor: any, groupName: string, _cellCount: number): { colorIndex: number; isObjectActor: boolean } {
    const prop = actor.getProperty();

    let colorIndex: number;
    let isObjectActor: boolean;
    if (groupName.includes('all_')) {
      isObjectActor = true;
      colorIndex = GlobalSettings.Instance.objIndex;
      prop.setColor(GlobalSettings.Instance.getColorForObject());
    } else {
      isObjectActor = false;
      colorIndex = GlobalSettings.Instance.grpIndex;
      prop.setColor(GlobalSettings.Instance.getColorForGroup());
      prop.setOpacity(1.0);
      actor.setVisibility(false);
    }

    const [r, g, b] = prop.getColor();
    prop.setEdgeVisibility(true);
    prop.setEdgeColor(r, g, b);
    prop.setLineWidth(0.3);
    prop.setInterpolationToPhong();
    prop.setAmbient(GlobalSettings.Instance.ambientIntensity);
    prop.setSpecular(GlobalSettings.Instance.specular);
    prop.setSpecularPower(GlobalSettings.Instance.specularPower);

    return { colorIndex, isObjectActor };
  }
}
