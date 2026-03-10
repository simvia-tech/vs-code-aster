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

  backgroundColor = [0.6627, 0.7960, 0.910];
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

  get isDark(): boolean {
    return document.body.classList.contains('vscode-dark') ||
           document.body.classList.contains('vscode-high-contrast');
  }

  private _meshGroupColors = [
    [0.902, 0.098, 0.294],
    [0.235, 0.706, 0.294],
    [1,     0.882, 0.098],
    [0.941, 0.196, 0.902],
    [0.961, 0.510, 0.192],
    [0.569, 0.118, 0.706],
    [0.275, 0.941, 0.941],
    [0.737, 0.965, 0.047],
    [0.980, 0.745, 0.745],
    [0,     0.502, 0.502],
    [0.902, 0.745, 1    ],
    [0.604, 0.388, 0.141],
    [0.263, 0.388, 0.847],
    [1,     0.980, 0.784],
    [0.502, 0,     0    ],
    [0.667, 1,     0.764],
    [0.502, 0.502, 0    ],
    [1,     0.847, 0.694],
    [0,     0,     0.463],
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
    [0.400, 0.620, 0.820],
    [0.280, 0.700, 0.580],
    [0.880, 0.560, 0.280],
    [0.600, 0.400, 0.800],
    [0.380, 0.720, 0.420],
    [0.820, 0.380, 0.440],
    [0.380, 0.680, 0.820],
    [0.820, 0.620, 0.380],
  ];

  private _objectColorsDark = [
    [0.440, 0.720, 0.980],
    [0.240, 0.880, 0.700],
    [0.980, 0.660, 0.320],
    [0.720, 0.500, 0.980],
    [0.400, 0.900, 0.500],
    [0.980, 0.420, 0.520],
    [0.360, 0.800, 0.980],
    [0.980, 0.740, 0.440],
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
