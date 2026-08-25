import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkCellArray from '@kitware/vtk.js/Common/Core/CellArray';
import { GlobalSettings } from '../../settings/GlobalSettings';
import { VtkApp } from '../../core/VtkApp';

export class FaceActorCreator {
  /** vtkPoints shared by every actor: one copy of the coordinates for the whole mesh. */
  private points: any;
  private cells: number[][];
  private cellsByGroup: number[][] = [];

  constructor(points: any, cells: number[][], cellIndexToGroup: number[]) {
    this.points = points;
    this.cells = cells;
    cellIndexToGroup.forEach((g, i) => {
      if (g >= 0) (this.cellsByGroup[g] ||= []).push(i);
    });
  }

  create(
    _groupName: string,
    groupId: number,
    isObject = false
  ): { actor: any; colorIndex: number; isObjectActor: boolean; cellCount: number } {
    const { polyData, cellCount } = this.prepare(groupId);

    const actor = vtkActor.newInstance();
    const mapper = vtkMapper.newInstance();

    mapper.setInputData(polyData);
    if (!isObject) {
      mapper.setResolveCoincidentTopologyToPolygonOffset();
      mapper.setRelativeCoincidentTopologyPolygonOffsetParameters(-2, -2);
    }
    actor.setMapper(mapper);

    const { colorIndex, isObjectActor } = this.setProperty(actor, isObject, cellCount);
    VtkApp.Instance.getRenderer().addActor(actor);

    return { actor, colorIndex, isObjectActor, cellCount };
  }

  private prepare(groupId: number): { polyData: any; cellCount: number } {
    const pd = vtkPolyData.newInstance();
    pd.setPoints(this.points);

    const cellIndices = this.cellsByGroup[groupId] ?? [];
    const cellCount = cellIndices.length;
    if (cellCount > 0) {
      const cellArray = vtkCellArray.newInstance({
        values: Uint32Array.from(
          cellIndices.flatMap((i) => {
            const c = this.cells[i];
            return [c.length, ...c];
          })
        ),
      });
      pd.setPolys(cellArray);
    }

    return { polyData: pd, cellCount };
  }

  private setProperty(
    actor: any,
    isObject: boolean,
    _cellCount: number
  ): { colorIndex: number; isObjectActor: boolean } {
    const prop = actor.getProperty();

    let colorIndex: number;
    let isObjectActor: boolean;
    if (isObject) {
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
    prop.setSpecular(0);

    return { colorIndex, isObjectActor };
  }
}
