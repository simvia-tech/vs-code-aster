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
    _readEditorBackground() {
        const raw = getComputedStyle(document.body).getPropertyValue("--vscode-editor-background").trim();
        const match = raw.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
        if (match) {
            return [parseInt(match[1], 16) / 255, parseInt(match[2], 16) / 255, parseInt(match[3], 16) / 255];
        }
        return [0.4, 0.6, 1.0];
    }

    updateBackground() {
        this.renderer.setBackground(this._readEditorBackground());
    }

    init(scene) {
        if (!window.vtk) {return;}

        this.fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
            rootContainer: scene,
            background: this._readEditorBackground(),
        });

        this.renderer = this.fullScreenRenderer.getRenderer();
        this.renderWindow = this.fullScreenRenderer.getRenderWindow();

        this.updateCameraOffset();

        // Keep the offset in sync if the window or sidebar resizes
        const controls = document.getElementById("controls");
        new ResizeObserver(() => this.updateCameraOffset()).observe(controls);
        window.addEventListener("resize", () => this.updateCameraOffset());

        // Refresh scene colors when VS Code theme changes
        new MutationObserver(() => {
            this.updateBackground();
            Controller.Instance.refreshThemeColors();
            this.renderWindow.render();
        }).observe(document.body, { attributes: true, attributeFilter: ["class"] });

        Controller.Instance.getVSCodeAPI().postMessage({
            type: 'debugPanel',
            text: 'vtkAppInitialized'
        });
    }

    /**
     * Offsets the camera so the scene appears centered in the area to the right of the sidebar.
     * Also repositions the zoom widget to the center of that same area.
     */
    updateCameraOffset() {
        const sidebarWidth = document.getElementById("controls").offsetWidth;
        const offset = sidebarWidth / window.innerWidth;
        this.renderer.getActiveCamera().setWindowCenter(-offset, 0);
        this.renderWindow.render();

        const zoomWidget = document.getElementById("zoomWidget");
        if (zoomWidget) {
            zoomWidget.style.left = `${sidebarWidth + (window.innerWidth - sidebarWidth) / 2}px`;
        }
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
