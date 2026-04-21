import type { EdgeMode } from '../state';

export class GlobalSettings {
  private static _instance: GlobalSettings;

  static get Instance(): GlobalSettings {
    if (!this._instance) {
      this._instance = new GlobalSettings();
    }
    return this._instance;
  }

  grpIndex = 0;
  objIndex = 0;

  backgroundColor = [0.6627, 0.796, 0.91];
  ambientLightColor = [0.2, 0.2, 0.2];
  lightColor = [0.6667, 0.6667, 0.6667];
  surfaceInsideColor = [1, 1, 0];
  surfaceOutsideColor = [0.537, 0.529, 0.529];
  localSelectedColor = [1, 1, 1];
  surfaceTransparentColor = [0.553, 0.749, 0.42];
  surfaceRenderOrder = 0;
  wireframeColor = [0, 0, 0];
  wireframeOpacity = 0.35;
  wireframeAlpha = 1;
  wireframeRenderOrder = 10;
  wireframeSelectedColor = [1, 1, 1];
  wireframeSelectedRenderOrder = 11;
  drawLineColor = [1, 0, 0];
  drawLineHelperRenderOrder = 12;
  selectHelperColor = [1, 1, 1];
  selectionPointColor = [1, 0, 0];

  hiddenObjectOpacity = 0;
  edgeMode: EdgeMode = 'threshold';
  edgeThresholdMultiplier = 1;
  specular = 0.3;
  specularPower = 15;
  ambientIntensity = 0.1;
  edgeOpacity = 0.7;
  edgeGroupThickness = 3;
  edgeGroupDepthOffset = true;
  nodeGroupSize = 1;
  sidebarSort: 'natural' | 'size' = 'natural';
  groupByKind = true;
  groupTransparency = 0.2;
  showOrientationWidget = true;
  showBoundingBox = false;
  showWireframe = false;

  get isDark(): boolean {
    return (
      document.body.classList.contains('vscode-dark') ||
      document.body.classList.contains('vscode-high-contrast')
    );
  }

  private _meshGroupColors = [
    [0.902, 0.098, 0.294],
    [0.235, 0.706, 0.294],
    [1, 0.882, 0.098],
    [0.941, 0.196, 0.902],
    [0.961, 0.51, 0.192],
    [0.569, 0.118, 0.706],
    [0.275, 0.941, 0.941],
    [0.737, 0.965, 0.047],
    [0.98, 0.745, 0.745],
    [0, 0.502, 0.502],
    [0.902, 0.745, 1],
    [0.604, 0.388, 0.141],
    [0.263, 0.388, 0.847],
    [1, 0.98, 0.784],
    [0.502, 0, 0],
    [0.667, 1, 0.764],
    [0.502, 0.502, 0],
    [1, 0.847, 0.694],
    [0, 0, 0.463],
    [0.502, 0.502, 0.502],
  ];

  get meshGroupColors(): number[][] {
    if (this.isDark) return this._meshGroupColors;
    return this._meshGroupColors.map(([r, g, b]) => [r * 0.72, g * 0.72, b * 0.72]);
  }

  getColorForGroup(): number[] {
    const idx = this.grpIndex % this._meshGroupColors.length;
    this.grpIndex++;
    return this.meshGroupColors[idx];
  }

  private _objectColorsLight = [
    [0.4, 0.62, 0.82],
    [0.28, 0.7, 0.58],
    [0.88, 0.56, 0.28],
    [0.6, 0.4, 0.8],
    [0.38, 0.72, 0.42],
    [0.82, 0.38, 0.44],
    [0.38, 0.68, 0.82],
    [0.82, 0.62, 0.38],
  ];

  private _objectColorsDark = [
    [0.44, 0.72, 0.98],
    [0.24, 0.88, 0.7],
    [0.98, 0.66, 0.32],
    [0.72, 0.5, 0.98],
    [0.4, 0.9, 0.5],
    [0.98, 0.42, 0.52],
    [0.36, 0.8, 0.98],
    [0.98, 0.74, 0.44],
  ];

  get objectColors(): number[][] {
    return this.isDark ? this._objectColorsDark : this._objectColorsLight;
  }

  getColorForObject(): number[] {
    const idx = this.objIndex % this.objectColors.length;
    this.objIndex++;
    return this.objectColors[idx];
  }
}
