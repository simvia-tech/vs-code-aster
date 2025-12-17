class NodeActorCreator {
  /**
   * @param {Vector[]} vertices - List of vertex coordinates
   * @param {number[][]} nodes - 
   * @param {number[]} nodeIndexToGroup - Node-to-group index mapping
   */
  constructor(vertices, nodes, nodeIndexToGroup) {
    this.vertices = vertices;
    this.nodes = nodes;
    this.nodeIndexToGroup = nodeIndexToGroup;
  }

  /**
   * Creates and configures an actor for a face group.
   * @param {number} groupId
   * @returns {vtkActor}
   */
  create(groupId) {

    const polyData = this.prepare(groupId);
    
    const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
    mapper.setInputData(polyData);
    
    const actor = vtk.Rendering.Core.vtkActor.newInstance();
    actor.setMapper(mapper);

    this.setProperty(actor);
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

  const nodeIndices = this.nodeIndexToGroup
    .map((g, idx) => (g === groupId ? idx : -1))
    .filter(idx => idx !== -1);

  if (nodeIndices.length > 0) {
    const pts = vtk.Common.Core.vtkPoints.newInstance();
    const data = [];

    for (const idx of nodeIndices) {
      const v = this.vertices[this.nodes[idx]];
      if (v) {
        data.push(v.x, v.y, v.z);
      }
    }

    pts.setData(Float32Array.from(data), 3);
    pd.setPoints(pts);
    
    const numPoints = data.length / 3;
    const verts = vtk.Common.Core.vtkCellArray.newInstance();
    const vertData = [];
    
    for (let i = 0; i < numPoints; i++) {
      vertData.push(1, i); 
    }
    
    verts.setData(Uint32Array.from(vertData));
    pd.setVerts(verts);
    
  }

  return pd;
}

  /**
   * Initialize rendering properties (color, opacity, visibility)
   * @param {vtkActor} actor
   * @param {string} groupName
   */
  setProperty(actor) {
    const prop = actor.getProperty();
    prop.setRepresentation(0);
    prop.setOpacity(1);
    actor.setVisibility(false);
    prop.setColor(GlobalSettings.Instance.getColorForGroup());
  }
  
}
