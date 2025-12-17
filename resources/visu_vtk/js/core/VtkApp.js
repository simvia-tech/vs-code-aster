/**
 * Singleton managing the VTK rendering context.
 * Handles the creation of renderer and render window for the visualization panel.
 */
class VtkApp {

    static get Instance() {
        if (!this._i) {
            this._i = new VtkApp();
        }
        return this._i;
    }

    /**
     * Initializes the full-screen renderer in the given HTML scene
     * @param {HTMLElement} scene - The HTML element to attach the renderer
     */
    init(scene) {
        if (!window.vtk) {return;}

        this.fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
            rootContainer: scene,
            background: [0.4, 0.6, 1.0], 
        });

        this.renderer = this.fullScreenRenderer.getRenderer();
        this.renderWindow = this.fullScreenRenderer.getRenderWindow();

        Controller.Instance.getVSCodeAPI().postMessage({ 
            type: 'debugPanel', 
            text: 'vtkAppInitialized' 
        });
    }

    /** @returns {vtkRenderer} The VTK renderer */
    getRenderer() {
        return this.renderer;
    }

    /** @returns {vtkRenderWindow} The VTK render window */
    getRenderWindow() {
        return this.renderWindow;
    }
}
