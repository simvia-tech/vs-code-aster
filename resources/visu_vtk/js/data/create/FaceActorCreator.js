class FaceActorCreator {
  /**
   * Create a FaceActorCreator.
   * @param {Vector[]} vertices - List of vertex coordinates
   * @param {number[][]} cells - Connectivity list
   * @param {number[]} cellIndexToGroup - Cell-to-group index mapping
   */
  constructor(vertices, cells, cellIndexToGroup) {
    this.vertices = vertices;
    this.cells = cells;
    this.cellIndexToGroup = cellIndexToGroup;
  }

  /**
   * Creates and configures an actor for a face group.
   * @param {string} groupName
   * @param {number} groupId
   * @returns {vtkActor}
   */
  create(groupName, groupId) {
    const polyData = this.prepare(groupId);

    const actor = vtk.Rendering.Core.vtkActor.newInstance();
    const mapper = vtk.Rendering.Core.vtkMapper.newInstance();

    mapper.setInputData(polyData);
    actor.setMapper(mapper);

    this.setProperty(actor, groupName);
    VtkApp.Instance.getRenderer().addActor(actor);

    return actor;
  }

  
  /**
   * Prepares vtkPolyData for a given groupId using instance data.
   * @param {number} groupId
   * @returns {vtkPolyData}
   */
  prepare(groupId) {
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
      .filter(idx => idx !== -1);

    if (cellIndices.length > 0) {
      const cellArray = vtk.Common.Core.vtkCellArray.newInstance({
        values: Uint32Array.from(cellIndices.flatMap(i => {
          const c = this.cells[i];
          return [c.length, ...c];
        }))
      });
      pd.setPolys(cellArray);
    }

    return pd;
  }

  /**
   * Configures rendering properties (color, opacity, visibility)
   * @param {vtkActor} actor
   * @param {string} groupName
   */
  setProperty(actor, groupName) {
    const prop = actor.getProperty();

    if (groupName.includes("all_")) {
      prop.setColor(GlobalSettings.Instance.surfaceOutsideColor);
    } else {
      prop.setColor(GlobalSettings.Instance.getColorForGroup());
      prop.setOpacity(0.8);
      actor.setVisibility(false);
    }

    prop.setEdgeVisibility(true);
    prop.setLineWidth(0.3);
    prop.setInterpolationToPhong();
    prop.setSpecular(0.3);
    prop.setSpecularPower(15);
  }
  
}
