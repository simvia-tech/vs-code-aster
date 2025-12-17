/**
 * Creates custom XYZ axes actors with colored cylinders and spheres for visualization.
 * Provides utility to generate axes for VTK rendering.
 */
class CustomAxesCreator {
  constructor() {
    this.axisLength = 1.0;
    this.axisRadius = 0.02;
    this.sphereRadius = 0.08;

    this.colors = {
      x: [1, 0, 0],
      y: [0.251, 0.529, 0.376], 
      z: [0, 0, 1]  
    };
  }

  /**
   * Creates a single actor containing X, Y, Z axes with spheres at the ends.
   * @returns {vtkActor} - VTK actor containing all axes
   */
  static createCustomAxesActor() {
    const instance = new CustomAxesCreator();

    const axisRadius = instance.axisRadius;
    const sphereRadius = 0.1;
    const sphereTheta = 12;
    const spherePhi = 12;

    const addColor = (polyData, color) => {
      const scalars = vtk.Common.Core.vtkDataArray.newInstance({
        numberOfComponents: 3,
        values: new Uint8Array(polyData.getPoints().getNumberOfPoints() * 3),
        name: 'color'
      });

      const colors = scalars.getData();
      const rgb = color.map(c => Math.round(c * 255));
      for (let i = 0; i < colors.length; i += 3) {
        colors[i] = rgb[0];
        colors[i + 1] = rgb[1];
        colors[i + 2] = rgb[2];
      }

      polyData.getPointData().setScalars(scalars);
    };

    const xAxisSource = vtk.Filters.General.vtkAppendPolyData.newInstance();
    xAxisSource.setInputData(vtk.Filters.Sources.vtkCylinderSource.newInstance({
      radius: axisRadius,
      resolution: 20,
      direction: [1, 0, 0],
      center: [0.5, 0, 0]
    }).getOutputData());

    xAxisSource.addInputData(vtk.Filters.Sources.vtkSphereSource.newInstance({
      radius: sphereRadius,
      center: [1, 0, 0],
      thetaResolution: sphereTheta,
      phiResolution: spherePhi
    }).getOutputData());

    const xAxis = xAxisSource.getOutputData();
    addColor(xAxis, instance.colors.x);

    const yAxisSource = vtk.Filters.General.vtkAppendPolyData.newInstance();
    yAxisSource.setInputData(vtk.Filters.Sources.vtkCylinderSource.newInstance({
      radius: axisRadius,
      resolution: 20,
      direction: [0, 1, 0],
      center: [0, 0.5, 0]
    }).getOutputData());

    yAxisSource.addInputData(vtk.Filters.Sources.vtkSphereSource.newInstance({
      radius: sphereRadius,
      center: [0, 1, 0],
      thetaResolution: sphereTheta,
      phiResolution: spherePhi
    }).getOutputData());

    const yAxis = yAxisSource.getOutputData();
    addColor(yAxis, instance.colors.y);

    const zAxisSource = vtk.Filters.General.vtkAppendPolyData.newInstance();
    zAxisSource.setInputData(vtk.Filters.Sources.vtkCylinderSource.newInstance({
      radius: axisRadius,
      resolution: 20,
      direction: [0, 0, 1],
      center: [0, 0, 0.5]
    }).getOutputData());

    zAxisSource.addInputData(vtk.Filters.Sources.vtkSphereSource.newInstance({
      radius: sphereRadius,
      center: [0, 0, 1],
      thetaResolution: sphereTheta,
      phiResolution: spherePhi
    }).getOutputData());

    const zAxis = zAxisSource.getOutputData();
    addColor(zAxis, instance.colors.z);

    // Combine all axes
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

  createAxisWithSphere(axis) {
    const start = [0, 0, 0];
    const end = [0, 0, 0];
    end[['x', 'y', 'z'].indexOf(axis)] = this.axisLength;

    const cylinderSource = vtk.Filters.Sources.vtkCylinderSource.newInstance({
      height: this.axisLength,
      radius: this.axisRadius,
      resolution: 16
    });
    const cylinderMapper = vtk.Rendering.Core.vtkMapper.newInstance();
    cylinderMapper.setInputConnection(cylinderSource.getOutputPort());
    const cylinderActor = vtk.Rendering.Core.vtkActor.newInstance();
    cylinderActor.setMapper(cylinderMapper);
    cylinderActor.getProperty().setColor(...this.colors[axis]);
    this.positionCylinder(cylinderActor, start, end);

    const sphereSource = vtk.Filters.Sources.vtkSphereSource.newInstance({
      radius: this.sphereRadius,
      thetaResolution: 16,
      phiResolution: 16
    });
    const sphereMapper = vtk.Rendering.Core.vtkMapper.newInstance();
    sphereMapper.setInputConnection(sphereSource.getOutputPort());
    const sphereActor = vtk.Rendering.Core.vtkActor.newInstance();
    sphereActor.setMapper(sphereMapper);
    sphereActor.setPosition(...end);
    sphereActor.getProperty().setColor(...this.colors[axis]);

    return { cylinder: cylinderActor, sphere: sphereActor };
  }

  positionCylinder(actor, start, end) {
    const center = [
      (start[0] + end[0]) / 2,
      (start[1] + end[1]) / 2,
      (start[2] + end[2]) / 2
    ];

    const direction = [
      end[0] - start[0],
      end[1] - start[1],
      end[2] - start[2]
    ];

    const length = Math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2);
    const normalized = direction.map(d => d / length);

    const yAxis = [0, 1, 0];
    const rotationAxis = [
      yAxis[1] * normalized[2] - yAxis[2] * normalized[1],
      yAxis[2] * normalized[0] - yAxis[0] * normalized[2],
      yAxis[0] * normalized[1] - yAxis[1] * normalized[0]
    ];

    const dotProduct = yAxis[0] * normalized[0] + yAxis[1] * normalized[1] + yAxis[2] * normalized[2];
    const angle = Math.acos(dotProduct) * (180 / Math.PI);

    actor.setPosition(...center);

    const axisLength = Math.sqrt(rotationAxis[0] ** 2 + rotationAxis[1] ** 2 + rotationAxis[2] ** 2);
    if (axisLength > 0.0001) {
      actor.rotateWXYZ(angle, ...rotationAxis.map(a => a / axisLength));
    }
  }
}
