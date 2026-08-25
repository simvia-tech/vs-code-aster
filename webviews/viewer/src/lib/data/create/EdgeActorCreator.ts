import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkCellArray from '@kitware/vtk.js/Common/Core/CellArray';
import { GlobalSettings } from '../../settings/GlobalSettings';
import { VtkApp } from '../../core/VtkApp';

export class EdgeActorCreator {
  /** vtkPoints shared by every actor: one copy of the coordinates for the whole mesh. */
  private points: any;
  private edges: number[][];
  private edgesByGroup: number[][] = [];

  constructor(points: any, edges: number[][], edgeIndexToGroup: number[]) {
    this.points = points;
    this.edges = edges;
    edgeIndexToGroup.forEach((g, i) => {
      if (g >= 0) (this.edgesByGroup[g] ||= []).push(i);
    });
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

  createStandalone(
    edgeIndices: number[],
    color: number[]
  ): { actor: any; contourActor: any; cellCount: number } | null {
    if (edgeIndices.length === 0) return null;

    const pd = this.buildPolyData(edgeIndices);

    const contourMapper = vtkMapper.newInstance();
    contourMapper.setInputData(pd);
    contourMapper.setResolveCoincidentTopologyToPolygonOffset();
    contourMapper.setRelativeCoincidentTopologyLineOffsetParameters(2, 2);
    const contourActor = vtkActor.newInstance();
    contourActor.setMapper(contourMapper);
    const contourProp = contourActor.getProperty();
    contourProp.setColor(0, 0, 0);
    contourProp.setLineWidth(4);
    contourProp.setLighting(false);
    VtkApp.Instance.getRenderer().addActor(contourActor);

    const mapper = vtkMapper.newInstance();
    mapper.setInputData(pd);
    EdgeActorCreator.applyDepthOffset(mapper, false);

    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);

    const prop = actor.getProperty();
    prop.setColor(color[0], color[1], color[2]);
    prop.setLineWidth(2);
    prop.setLighting(false);

    VtkApp.Instance.getRenderer().addActor(actor);
    return { actor, contourActor, cellCount: edgeIndices.length };
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

  private buildPolyData(edgeIndices: number[]): any {
    const pd = vtkPolyData.newInstance();
    pd.setPoints(this.points);
    if (edgeIndices.length > 0) {
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
    return pd;
  }

  private prepare(groupId: number): { polyData: any; cellCount: number } {
    const edgeIndices = this.edgesByGroup[groupId] ?? [];
    return { polyData: this.buildPolyData(edgeIndices), cellCount: edgeIndices.length };
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
