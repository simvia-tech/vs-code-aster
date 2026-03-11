import { Controller } from '../Controller';

export class VtkApp {
  private static _i: VtkApp;
  private fullScreenRenderer: any;
  renderer: any;
  renderWindow: any;

  static get Instance(): VtkApp {
    if (!this._i) {
      this._i = new VtkApp();
    }
    return this._i;
  }

  private _readEditorBackground(): number[] {
    const raw = getComputedStyle(document.body).getPropertyValue('--vscode-editor-background').trim();
    const match = raw.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
    if (match) {
      return [parseInt(match[1], 16) / 255, parseInt(match[2], 16) / 255, parseInt(match[3], 16) / 255];
    }
    return [0.4, 0.6, 1.0];
  }

  updateBackground(): void {
    this.renderer.setBackground(this._readEditorBackground());
  }

  init(scene: HTMLElement): void {
    if (!window.vtk) { return; }

    this.fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
      rootContainer: scene,
      background: this._readEditorBackground(),
    });

    this.renderer = this.fullScreenRenderer.getRenderer();
    this.renderWindow = this.fullScreenRenderer.getRenderWindow();

    this.updateCameraOffset();

    const controls = document.getElementById('controls');
    if (controls) {
      new ResizeObserver(() => this.updateCameraOffset()).observe(controls);
    }
    window.addEventListener('resize', () => this.updateCameraOffset());

    new MutationObserver(() => {
      this.updateBackground();
      Controller.Instance.refreshThemeColors();
      this.renderWindow.render();
    }).observe(document.body, { attributes: true, attributeFilter: ['class'] });

    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'debugPanel',
      text: 'vtkAppInitialized',
    });
  }

  updateCameraOffset(): void {
    if (!this.renderer) return;
    const controls = document.getElementById('controls');
    const sidebarActions = document.getElementById('sidebarActions');
    const sidebarWidth = controls
      ? controls.offsetWidth - (sidebarActions?.offsetWidth ?? 0)
      : 0;
    const offset = sidebarWidth / window.innerWidth;
    this.renderer.getActiveCamera().setWindowCenter(-offset, 0);
    this.renderWindow.render();

    const zoomWidget = document.getElementById('zoomWidget');
    if (zoomWidget) {
      zoomWidget.style.left = `${sidebarWidth + (window.innerWidth - sidebarWidth) / 2}px`;
    }
  }

  getRenderer(): any {
    return this.renderer;
  }

  getRenderWindow(): any {
    return this.renderWindow;
  }
}
