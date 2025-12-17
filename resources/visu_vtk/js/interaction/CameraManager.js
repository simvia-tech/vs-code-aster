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

        const renderer = VtkApp.Instance.getRenderer();
        this.camera = renderer.getActiveCamera();
        this.lastDistance = this.camera.getDistance();

        // Store only node groups
        for (const [groupName, group] of Object.entries(groups)) {
            if (!group.isFaceGroup) {
                this.nodesGroups[groupName] = group;
                group.setSize(this.lastDistance);
            }
        }

        this.axisMarker = this.createAxisMarker();
        this.activateSizeUpdate();
    }

    /**
     * Automatically updates node group sizes when the camera distance changes
     */
    activateSizeUpdate() {
        this.camera.onModified(() => {
            const currentDistance = this.camera.getDistance();
            if (Math.abs(currentDistance - this.lastDistance) > 1e-2) {
                for (const nodeGroup of Object.values(this.nodesGroups)) {
                    nodeGroup.setSize(currentDistance);
                }
                this.lastDistance = currentDistance;
            }
        });
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
