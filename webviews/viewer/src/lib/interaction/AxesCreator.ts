export class AxesCreator {
  private axisRadius = 0.02;

  private colors = {
    x: [1, 0, 0],
    y: [0.251, 0.529, 0.376],
    z: [0, 0, 1],
  };

  static createCustomAxesActor(): any {
    const instance = new AxesCreator();

    const axisRadius = instance.axisRadius;
    const sphereRadius = 0.1;
    const sphereTheta = 12;
    const spherePhi = 12;

    const addColor = (polyData: any, color: number[]) => {
      const scalars = vtk.Common.Core.vtkDataArray.newInstance({
        numberOfComponents: 3,
        values: new Uint8Array(polyData.getPoints().getNumberOfPoints() * 3),
        name: 'color',
      });

      const colors = scalars.getData();
      const rgb = color.map((c) => Math.round(c * 255));
      for (let i = 0; i < colors.length; i += 3) {
        colors[i] = rgb[0];
        colors[i + 1] = rgb[1];
        colors[i + 2] = rgb[2];
      }

      polyData.getPointData().setScalars(scalars);
    };

    const xAxisSource = vtk.Filters.General.vtkAppendPolyData.newInstance();
    xAxisSource.setInputData(
      vtk.Filters.Sources.vtkCylinderSource
        .newInstance({
          radius: axisRadius,
          resolution: 20,
          direction: [1, 0, 0],
          center: [0.5, 0, 0],
        })
        .getOutputData()
    );
    xAxisSource.addInputData(
      vtk.Filters.Sources.vtkSphereSource
        .newInstance({
          radius: sphereRadius,
          center: [1, 0, 0],
          thetaResolution: sphereTheta,
          phiResolution: spherePhi,
        })
        .getOutputData()
    );
    const xAxis = xAxisSource.getOutputData();
    addColor(xAxis, instance.colors.x);

    const yAxisSource = vtk.Filters.General.vtkAppendPolyData.newInstance();
    yAxisSource.setInputData(
      vtk.Filters.Sources.vtkCylinderSource
        .newInstance({
          radius: axisRadius,
          resolution: 20,
          direction: [0, 1, 0],
          center: [0, 0.5, 0],
        })
        .getOutputData()
    );
    yAxisSource.addInputData(
      vtk.Filters.Sources.vtkSphereSource
        .newInstance({
          radius: sphereRadius,
          center: [0, 1, 0],
          thetaResolution: sphereTheta,
          phiResolution: spherePhi,
        })
        .getOutputData()
    );
    const yAxis = yAxisSource.getOutputData();
    addColor(yAxis, instance.colors.y);

    const zAxisSource = vtk.Filters.General.vtkAppendPolyData.newInstance();
    zAxisSource.setInputData(
      vtk.Filters.Sources.vtkCylinderSource
        .newInstance({
          radius: axisRadius,
          resolution: 20,
          direction: [0, 0, 1],
          center: [0, 0, 0.5],
        })
        .getOutputData()
    );
    zAxisSource.addInputData(
      vtk.Filters.Sources.vtkSphereSource
        .newInstance({
          radius: sphereRadius,
          center: [0, 0, 1],
          thetaResolution: sphereTheta,
          phiResolution: spherePhi,
        })
        .getOutputData()
    );
    const zAxis = zAxisSource.getOutputData();
    addColor(zAxis, instance.colors.z);

    const axesSource = vtk.Filters.General.vtkAppendPolyData.newInstance();
    axesSource.setInputData(xAxis);
    axesSource.addInputData(yAxis);
    axesSource.addInputData(zAxis);

    const axesMapper = vtk.Rendering.Core.vtkMapper.newInstance();
    axesMapper.setInputData(axesSource.getOutputData());

    const axesActor = vtk.Rendering.Core.vtkActor.newInstance();
    axesActor.setMapper(axesMapper);
    axesActor.getProperty().setLighting(false);

    return axesActor;
  }
}
