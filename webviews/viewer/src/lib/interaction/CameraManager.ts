import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkPixelSpaceCallbackMapper from '@kitware/vtk.js/Rendering/Core/PixelSpaceCallbackMapper';
import vtkAppendPolyData from '@kitware/vtk.js/Filters/General/AppendPolyData';
import vtkSphereSource from '@kitware/vtk.js/Filters/Sources/SphereSource';
import vtkOrientationMarkerWidget from '@kitware/vtk.js/Interaction/Widgets/OrientationMarkerWidget';
import { Corners } from '@kitware/vtk.js/Interaction/Widgets/OrientationMarkerWidget/Constants';
import { VtkApp } from '../core/VtkApp';
import { AxesCreator } from './AxesCreator';
import { GlobalSettings } from '../settings/GlobalSettings';
import { zoomRatio, isAtDefaultZoom, boundingBoxDimensions } from '../state';
import type { Group } from '../data/Group';

export class CameraManager {
  private static _i: CameraManager;
  private camera: any;
  private initialDistance = 0;
  private lastDistance = 0;
  nodesGroups: Record<string, Group> = {};
  faceGroups: Record<string, Group> = {};
  private orientationWidget: any;
  private boundingBoxActors: any[] = [];
  private boundingBoxDotsActor: any = null;

  static get Instance(): CameraManager {
    if (!this._i) {
      this._i = new CameraManager();
    }
    return this._i;
  }

  init(groups: Record<string, Group>): void {
    this.nodesGroups = {};
    this.faceGroups = {};

    const renderer = VtkApp.Instance.getRenderer();
    this.camera = renderer.getActiveCamera();
    this.initialDistance = this.camera.getDistance();
    this.lastDistance = this.initialDistance;

    for (const [groupName, group] of Object.entries(groups)) {
      if (group.kind === 'node') {
        this.nodesGroups[groupName] = group;
        group.setSize(this.lastDistance);
      } else if (group.isSurfaceGroup && group.cellCount !== null) {
        this.faceGroups[groupName] = group;
        group.updateEdgeVisibility(this.lastDistance, this.initialDistance);
      }
    }

    this._updateZoomIndicator(this.initialDistance);
    this.createAxisMarker();
    this.createBoundingBox(groups);
    this.activateSizeUpdate();

    if (GlobalSettings.Instance.showWireframe) {
      this.setWireframeMode(true);
    }
  }

  private activateSizeUpdate(): void {
    this.camera.onModified(() => {
      const currentDistance = this.camera.getDistance();
      this._updateZoomIndicator(currentDistance);
      if (Math.abs(currentDistance - this.lastDistance) > 1e-2) {
        for (const nodeGroup of Object.values(this.nodesGroups)) {
          nodeGroup.setSize(currentDistance);
        }
        for (const faceGroup of Object.values(this.faceGroups)) {
          faceGroup.updateEdgeVisibility(currentDistance, this.initialDistance);
        }
        this.lastDistance = currentDistance;
      }
    });
  }

  private _updateZoomIndicator(currentDistance: number): void {
    const ratio = this.initialDistance / currentDistance;
    let text: string;
    if (ratio >= 10) text = `${Math.round(ratio)}×`;
    else if (ratio >= 1) text = `${ratio.toFixed(1)}×`;
    else text = `${ratio.toFixed(2)}×`;

    zoomRatio.set(ratio);
    isAtDefaultZoom.set(Math.abs(ratio - 1) < 0.01);

    const zoomIndicator = document.getElementById('zoomIndicator');
    if (zoomIndicator) zoomIndicator.textContent = text;
  }

  resetZoom(): void {
    VtkApp.Instance.getRenderer().resetCamera();
    VtkApp.Instance.updateCameraOffset();
  }

  setZoom(ratio: number): void {
    const focalPoint = this.camera.getFocalPoint();
    const position = this.camera.getPosition();
    const dx = position[0] - focalPoint[0];
    const dy = position[1] - focalPoint[1];
    const dz = position[2] - focalPoint[2];
    const currentDist = Math.sqrt(dx * dx + dy * dy + dz * dz);
    const scale = this.initialDistance / ratio / currentDist;
    this.camera.setPosition(
      focalPoint[0] + dx * scale,
      focalPoint[1] + dy * scale,
      focalPoint[2] + dz * scale
    );
    VtkApp.Instance.getRenderer().resetCameraClippingRange();
    VtkApp.Instance.updateCameraOffset();
  }

  refreshEdgeVisibility(): void {
    for (const faceGroup of Object.values(this.faceGroups)) {
      faceGroup.updateEdgeVisibility(this.lastDistance, this.initialDistance);
    }
    VtkApp.Instance.getRenderWindow().render();
  }

  refreshNodeGroupSize(): void {
    for (const nodeGroup of Object.values(this.nodesGroups)) {
      nodeGroup.setSize(this.lastDistance);
    }
    VtkApp.Instance.getRenderWindow().render();
  }

  setOrientationWidgetVisible(visible: boolean): void {
    this.orientationWidget.setEnabled(visible);
    VtkApp.Instance.getRenderWindow().render();
  }

  setBoundingBoxVisible(visible: boolean): void {
    for (const a of this.boundingBoxActors) a.setVisibility(visible);
    VtkApp.Instance.getRenderWindow().render();
  }

  refreshBoundingBoxTheme(): void {
    if (!this.boundingBoxDotsActor) return;
    const c = VtkApp.Instance.readEditorForeground();
    this.boundingBoxDotsActor.getProperty().setColor(c[0], c[1], c[2]);
  }

  setWireframeMode(wireframe: boolean): void {
    const rep = wireframe ? 1 : 2;
    for (const group of Object.values(this.faceGroups)) {
      group.actor.getProperty().setRepresentation(rep);
    }
    VtkApp.Instance.getRenderWindow().render();
  }

  setCameraAxis(axis: string): void {
    if (!this.camera) {
      return;
    }

    const focalPoint = this.camera.getFocalPoint();
    const distance = this.camera.getDistance();

    let newPosition = [0, 0, 0];
    let viewUp = [0, 0, 1];

    switch (axis.toLowerCase()) {
      case 'x':
        newPosition = [focalPoint[0] + distance, focalPoint[1], focalPoint[2]];
        break;
      case 'y':
        newPosition = [focalPoint[0], focalPoint[1] + distance, focalPoint[2]];
        break;
      case 'z':
        newPosition = [focalPoint[0], focalPoint[1], focalPoint[2] + distance];
        viewUp = [0, 1, 0];
        break;
      default:
        return;
    }

    this.camera.setPosition(...newPosition);
    this.camera.setViewUp(viewUp);
    VtkApp.Instance.getRenderer().resetCameraClippingRange();
    VtkApp.Instance.getRenderWindow().render();
  }

  private createAxisMarker(): any {
    const axes = AxesCreator.createCustomAxesActor();

    const widget = vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: VtkApp.Instance.getRenderWindow().getInteractor(),
    });
    widget.setEnabled(true);
    widget.setViewportCorner(Corners.BOTTOM_RIGHT);
    widget.setViewportSize(0.15);

    this.orientationWidget = widget;
    return axes;
  }

  private static readonly AXIS_COLORS = {
    x: [0.937, 0.267, 0.267],
    y: [0.133, 0.773, 0.369],
    z: [0.231, 0.51, 0.965],
  };

  private createBoundingBox(groups: Record<string, Group>): void {
    let xmin = Infinity;
    let xmax = -Infinity;
    let ymin = Infinity;
    let ymax = -Infinity;
    let zmin = Infinity;
    let zmax = -Infinity;

    for (const group of Object.values(groups)) {
      if (!group.isSurfaceGroup || group.fileGroup !== null) continue;
      const b = group.actor.getBounds();
      if (b[0] < xmin) xmin = b[0];
      if (b[1] > xmax) xmax = b[1];
      if (b[2] < ymin) ymin = b[2];
      if (b[3] > ymax) ymax = b[3];
      if (b[4] < zmin) zmin = b[4];
      if (b[5] > zmax) zmax = b[5];
    }

    if (!isFinite(xmin)) return;

    const bounds = [xmin, xmax, ymin, ymax, zmin, zmax];
    boundingBoxDimensions.set({ x: xmax - xmin, y: ymax - ymin, z: zmax - zmin });

    const renderer = VtkApp.Instance.getRenderer();
    const initiallyVisible = GlobalSettings.Instance.showBoundingBox;

    for (const a of this.boundingBoxActors) renderer.removeActor(a);
    this.boundingBoxActors = [];

    const register = (actor: any) => {
      renderer.addActor(actor);
      actor.setVisibility(initiallyVisible);
      this.boundingBoxActors.push(actor);
    };

    register(this.createAxisLines(bounds, 'x', CameraManager.AXIS_COLORS.x));
    register(this.createAxisLines(bounds, 'y', CameraManager.AXIS_COLORS.y));
    register(this.createAxisLines(bounds, 'z', CameraManager.AXIS_COLORS.z));

    const dots = this.createBoundingBoxDots(bounds);
    if (dots) {
      register(dots);
      this.boundingBoxDotsActor = dots;
    }

    const labels = this.createBoundingBoxLabelActor(bounds);
    if (labels) register(labels);
  }

  private createAxisLines(bounds: number[], axis: 'x' | 'y' | 'z', color: number[]): any {
    const [xmin, xmax, ymin, ymax, zmin, zmax] = bounds;
    let edges: number[][][];
    if (axis === 'x') {
      edges = [
        [
          [xmin, ymin, zmin],
          [xmax, ymin, zmin],
        ],
        [
          [xmin, ymax, zmin],
          [xmax, ymax, zmin],
        ],
        [
          [xmin, ymin, zmax],
          [xmax, ymin, zmax],
        ],
        [
          [xmin, ymax, zmax],
          [xmax, ymax, zmax],
        ],
      ];
    } else if (axis === 'y') {
      edges = [
        [
          [xmin, ymin, zmin],
          [xmin, ymax, zmin],
        ],
        [
          [xmax, ymin, zmin],
          [xmax, ymax, zmin],
        ],
        [
          [xmin, ymin, zmax],
          [xmin, ymax, zmax],
        ],
        [
          [xmax, ymin, zmax],
          [xmax, ymax, zmax],
        ],
      ];
    } else {
      edges = [
        [
          [xmin, ymin, zmin],
          [xmin, ymin, zmax],
        ],
        [
          [xmax, ymin, zmin],
          [xmax, ymin, zmax],
        ],
        [
          [xmin, ymax, zmin],
          [xmin, ymax, zmax],
        ],
        [
          [xmax, ymax, zmin],
          [xmax, ymax, zmax],
        ],
      ];
    }

    const points = new Float64Array(edges.length * 6);
    const lines = new Uint32Array(edges.length * 3);
    edges.forEach(([p1, p2], i) => {
      points[i * 6] = p1[0];
      points[i * 6 + 1] = p1[1];
      points[i * 6 + 2] = p1[2];
      points[i * 6 + 3] = p2[0];
      points[i * 6 + 4] = p2[1];
      points[i * 6 + 5] = p2[2];
      lines[i * 3] = 2;
      lines[i * 3 + 1] = i * 2;
      lines[i * 3 + 2] = i * 2 + 1;
    });

    const polyData = vtkPolyData.newInstance();
    polyData.getPoints().setData(points, 3);
    // The 2nd arg (numberOfComponents) is accepted at runtime but missing
    // from vtk.js's .d.ts for setData on line arrays.
    (polyData.getLines() as any).setData(lines, 1);

    const mapper = vtkMapper.newInstance();
    mapper.setInputData(polyData);
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setColor(color[0], color[1], color[2]);
    actor.getProperty().setLineWidth(2);
    actor.getProperty().setLighting(false);
    actor.setPickable(false);
    return actor;
  }

  private createBoundingBoxDots(bounds: number[]): any {
    const [xmin, xmax, ymin, ymax, zmin, zmax] = bounds;
    const dx = xmax - xmin;
    const dy = ymax - ymin;
    const dz = zmax - zmin;
    const diagonal = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (diagonal < 1e-9) return null;
    const radius = diagonal * 0.006;

    const corners: [number, number, number][] = [
      [xmin, ymin, zmin],
      [xmax, ymin, zmin],
      [xmin, ymax, zmin],
      [xmax, ymax, zmin],
      [xmin, ymin, zmax],
      [xmax, ymin, zmax],
      [xmin, ymax, zmax],
      [xmax, ymax, zmax],
    ];

    const append = vtkAppendPolyData.newInstance();
    corners.forEach((center, i) => {
      const sphere = vtkSphereSource.newInstance({
        center,
        radius,
        thetaResolution: 16,
        phiResolution: 16,
      });
      if (i === 0) append.setInputData(sphere.getOutputData());
      else append.addInputData(sphere.getOutputData());
    });

    const mapper = vtkMapper.newInstance();
    mapper.setInputData(append.getOutputData());
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    const c = VtkApp.Instance.readEditorForeground();
    actor.getProperty().setColor(c[0], c[1], c[2]);
    actor.getProperty().setLighting(false);
    actor.setPickable(false);
    return actor;
  }

  private createBoundingBoxLabelActor(bounds: number[]): any {
    const [xmin, xmax, ymin, ymax, zmin, zmax] = bounds;
    const dx = Math.max(xmax - xmin, 1e-6);
    const dy = Math.max(ymax - ymin, 1e-6);
    const dz = Math.max(zmax - zmin, 1e-6);
    const m = 0.08;
    const c = 0.03;
    const anchors = [
      [xmin - 0.04 * dx, ymin - 0.04 * dy, zmin - 0.04 * dz],
      [xmax + m * dx, ymin - c * dy, zmin - c * dz],
      [xmin - c * dx, ymax + m * dy, zmin - c * dz],
      [xmin - c * dx, ymin - c * dy, zmax + m * dz],
    ];

    const pts = new Float64Array(anchors.length * 3);
    anchors.forEach((p, i) => {
      pts[i * 3] = p[0];
      pts[i * 3 + 1] = p[1];
      pts[i * 3 + 2] = p[2];
    });
    const polyData = vtkPolyData.newInstance();
    polyData.getPoints().setData(pts, 3);

    const mapper = vtkPixelSpaceCallbackMapper.newInstance();
    mapper.setInputData(polyData);
    // The 5th argument (viewportSize) is passed at runtime but omitted from
    // the callback type in vtk.js's .d.ts.
    (mapper.setCallback as (cb: (...args: any[]) => any) => void)(
      (
        coordsList: number[][],
        _camera: unknown,
        _aspect: unknown,
        _zBuf: unknown,
        viewportSize: number[]
      ) => {
        const dpr = window.devicePixelRatio || 1;
        const hCanvas = viewportSize ? viewportSize[1] : window.innerHeight * dpr;
        const ids = ['bboxLabelOrigin', 'bboxLabelX', 'bboxLabelY', 'bboxLabelZ'];
        for (let i = 0; i < coordsList.length && i < ids.length; i++) {
          const el = document.getElementById(ids[i]);
          if (el) {
            el.style.left = `${coordsList[i][0] / dpr}px`;
            el.style.top = `${(hCanvas - coordsList[i][1]) / dpr}px`;
          }
        }
      }
    );

    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.setPickable(false);
    return actor;
  }
}
