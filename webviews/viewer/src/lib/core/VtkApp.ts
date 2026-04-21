import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import vtkFullScreenRenderWindow from '@kitware/vtk.js/Rendering/Misc/FullScreenRenderWindow';
import { Controller } from '../Controller';
import { CameraManager } from '../interaction/CameraManager';

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
    return this._readVscodeColor('--vscode-editor-background', [0.4, 0.6, 1.0]);
  }

  readEditorForeground(): number[] {
    return this._readVscodeColor('--vscode-editor-foreground', [0.85, 0.85, 0.85]);
  }

  private _readVscodeColor(variable: string, fallback: number[]): number[] {
    const raw = getComputedStyle(document.body).getPropertyValue(variable).trim();
    const match = raw.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
    if (match) {
      return [
        parseInt(match[1], 16) / 255,
        parseInt(match[2], 16) / 255,
        parseInt(match[3], 16) / 255,
      ];
    }
    return fallback;
  }

  updateBackground(): void {
    if (!this.renderer) return;
    if (this._transparent) {
      // With the WebGL canvas created in premultipliedAlpha mode, any RGB with
      // alpha 0 is an undefined state that the browser may composite as opaque.
      // Clearing to (0, 0, 0, 0) is the only reliable way to make untouched
      // pixels fully transparent, letting the dream shader canvas behind show.
      this.renderer.setBackground([0, 0, 0, 0]);
    } else {
      const [r, g, b] = this._readEditorBackground();
      this.renderer.setBackground([r, g, b, 1]);
    }
    this.renderWindow?.render();
  }

  private _transparent = false;

  setTransparentBackground(enabled: boolean): void {
    this._transparent = enabled;
    this.updateBackground();
  }

  init(scene: HTMLElement): void {
    const [r, g, b] = this._readEditorBackground();
    this.fullScreenRenderer = vtkFullScreenRenderWindow.newInstance({
      container: scene,
      background: [r, g, b, 1],
    });

    this.renderer = this.fullScreenRenderer.getRenderer();
    this.renderWindow = this.fullScreenRenderer.getRenderWindow();

    // vtk.js 35 turns on Order-Independent Transparency when the WebGL2 context
    // exposes EXT_color_buffer_half_float / EXT_color_buffer_float, and its
    // weighted compositor washes translucent colors against bright backgrounds.
    // Blocking the extension probe forces the OIT pass onto its own fallback
    // (plain SRC_ALPHA blending), which renders identically on dark and light
    // themes without losing any WebGL2 features elsewhere.
    const gl = this.fullScreenRenderer.getApiSpecificRenderWindow().get3DContext();
    if (gl) {
      const origGetExtension = gl.getExtension.bind(gl);
      gl.getExtension = (name: string) => {
        if (name === 'EXT_color_buffer_half_float' || name === 'EXT_color_buffer_float') {
          return null;
        }
        return origGetExtension(name);
      };
    }

    this.updateCameraOffset();

    const controls = document.getElementById('controls');
    if (controls) {
      new ResizeObserver(() => this.updateCameraOffset()).observe(controls);
    }
    window.addEventListener('resize', () => this.updateCameraOffset());

    new MutationObserver(() => {
      this.updateBackground();
      Controller.Instance.refreshThemeColors();
      // Re-derive mesh edge colors from the just-applied face colors. Without
      // this, edges retain their previous tint until the camera moves and the
      // zoom listener re-runs updateEdgeVisibility.
      CameraManager.Instance.refreshEdgeVisibility();
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
    const sidebarWidth = controls ? controls.offsetWidth - (sidebarActions?.offsetWidth ?? 0) : 0;
    const offset = sidebarWidth / window.innerWidth;
    this.renderer.getActiveCamera().setWindowCenter(-offset, 0);
    this.renderWindow.render();

    const centerX = sidebarWidth + (window.innerWidth - sidebarWidth) / 2;

    const zoomWidget = document.getElementById('zoomWidget');
    if (zoomWidget) {
      zoomWidget.style.left = `${centerX}px`;
    }

    const topToolbar = document.getElementById('topToolbar');
    if (topToolbar) {
      topToolbar.style.left = `${centerX}px`;
    }
  }

  getRenderer(): any {
    return this.renderer;
  }

  getRenderWindow(): any {
    return this.renderWindow;
  }
}
