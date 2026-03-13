import { VtkApp } from '../core/VtkApp';
import { AxesCreator } from './AxesCreator';
import { zoomRatio, isAtDefaultZoom } from '../state';
import type { Group } from '../data/Group';

export class CameraManager {
  private static _i: CameraManager;
  private camera: any;
  private initialDistance = 0;
  private lastDistance = 0;
  nodesGroups: Record<string, Group> = {};
  faceGroups: Record<string, Group> = {};
  private orientationWidget: any;
  private axesActor: any;

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
      if (!group.isFaceGroup) {
        this.nodesGroups[groupName] = group;
        group.setSize(this.lastDistance);
      } else if (group.cellCount !== null) {
        this.faceGroups[groupName] = group;
        group.updateEdgeVisibility(this.lastDistance, this.initialDistance);
      }
    }

    this._updateZoomIndicator(this.initialDistance);
    this.axesActor = this.createAxisMarker();
    this.activateSizeUpdate();
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
    const scale = (this.initialDistance / ratio) / currentDist;
    this.camera.setPosition(
      focalPoint[0] + dx * scale,
      focalPoint[1] + dy * scale,
      focalPoint[2] + dz * scale,
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

  setOrientationWidgetVisible(visible: boolean): void {
    this.orientationWidget.setEnabled(visible);
    VtkApp.Instance.getRenderWindow().render();
  }

  setCameraAxis(axis: string): void {
    if (!this.camera) { return; }

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

    const widget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: VtkApp.Instance.getRenderWindow().getInteractor(),
    });
    widget.setEnabled(true);
    widget.setViewportCorner(vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_RIGHT);
    widget.setViewportSize(0.15);

    this.orientationWidget = widget;
    return axes;
  }
}
