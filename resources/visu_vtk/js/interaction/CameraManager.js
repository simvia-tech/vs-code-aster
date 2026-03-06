/**
 * Manages the camera and node scaling in the VTK visualization.
 */
class CameraManager {

    static get Instance() {
        if (!this._i) {
            this._i = new CameraManager();
        }
        return this._i;
    }

    /**
     * Initializes camera manager with node groups, sets up axis marker and size updates.
     * @param {Object} groups - Map of groupName -> Group instances
     */
    init(groups) {
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

        this._zoomIndicator = document.getElementById("zoomIndicator");
        this._resetZoomBtn = document.getElementById("resetZoomBtn");
        this._updateZoomIndicator(this.initialDistance);

        this.axisMarker = this.createAxisMarker();
        this.activateSizeUpdate();
    }

    /**
     * Automatically updates node group sizes when the camera distance changes
     */
    activateSizeUpdate() {
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

    _updateZoomIndicator(currentDistance) {
        if (!this._zoomIndicator) return;
        const ratio = this.initialDistance / currentDistance;
        let text;
        if (ratio >= 10) text = `${Math.round(ratio)}×`;
        else if (ratio >= 1)  text = `${ratio.toFixed(1)}×`;
        else                  text = `${ratio.toFixed(2)}×`;
        this._zoomIndicator.textContent = text;
        const atDefault = Math.abs(ratio - 1) < 0.01;
        this._resetZoomBtn?.classList.toggle("hidden!", atDefault);
    }

    resetZoom() {
        VtkApp.Instance.getRenderer().resetCamera();
        VtkApp.Instance.updateCameraOffset(); // resets window center offset and renders
    }

    /**
     * Moves the camera to a specific zoom ratio relative to the initial position.
     * @param {number} ratio - e.g. 2 means 2× zoomed in from initial
     */
    setZoom(ratio) {
        const focalPoint = this.camera.getFocalPoint();
        const position   = this.camera.getPosition();
        const dx = position[0] - focalPoint[0];
        const dy = position[1] - focalPoint[1];
        const dz = position[2] - focalPoint[2];
        const currentDist = Math.sqrt(dx * dx + dy * dy + dz * dz);
        const scale = (this.initialDistance / ratio) / currentDist;
        this.camera.setPosition(
            focalPoint[0] + dx * scale,
            focalPoint[1] + dy * scale,
            focalPoint[2] + dz * scale
        );
        VtkApp.Instance.getRenderer().resetCameraClippingRange();
        VtkApp.Instance.updateCameraOffset();
    }

    /**
     * Re-applies edge visibility for all face groups using the current camera distance.
     * Call this when the edge mode setting changes.
     */
    refreshEdgeVisibility() {
        for (const faceGroup of Object.values(this.faceGroups)) {
            faceGroup.updateEdgeVisibility(this.lastDistance, this.initialDistance);
        }
        VtkApp.Instance.getRenderWindow().render();
    }

    /**
     * Positions the camera along a given axis relative to its focal point.
     * @param {string} axis - 'x', 'y', or 'z'
     */
    setCameraAxis(axis) {
        if (!this.camera) { return; }

        const focalPoint = this.camera.getFocalPoint();
        const distance = this.camera.getDistance();

        let newPosition = [0, 0, 0];
        let viewUp = [0, 0, 1];

        switch(axis.toLowerCase()) {
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

    /**
     * Creates an orientation marker widget with XYZ axes in the bottom-right corner.
     * @returns {vtkOrientationMarkerWidget}
     */
    createAxisMarker() {
        const axes = CustomAxesCreator.createCustomAxesActor();

        const widget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
            actor: axes,
            interactor: VtkApp.Instance.getRenderWindow().getInteractor(),
        });
        widget.setEnabled(true);
        widget.setViewportCorner(vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_RIGHT);
        widget.setViewportSize(0.15);
        
        this.orientationWidget = widget;
        this.axesActor = axes;
    }
}
