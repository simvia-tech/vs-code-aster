class GlobalSettings {
    static get Instance() {
        if (!this._instance) {
            this._instance = new GlobalSettings();
        }
        return this._instance;
    }

    constructor() {
        this.grpIndex = 0;
        this.objIndex = 0;
    }

    // scene
    backgroundColor = [0.6627, 0.7960, 0.910]; // #a9cbe8
    ambientLightColor = [0.2, 0.2, 0.2];       // #333333
    lightColor = [0.6667, 0.6667, 0.6667];    // #aaaaaa
    // app
    surfaceInsideColor = [1, 1, 0];            // #ffff00

    surfaceOutsideColor = [0.537, 0.529, 0.529]; // #898787
    localSelectedColor = [1, 1, 1];               // #ffffff
    surfaceTransparentColor = [0.553, 0.749, 0.42]; // #8dbf6b
    surfaceRenderOrder = 0;

    wireframeColor = [0, 0, 0]; // #000000
    wireframeOpacity = 0.35;
    wireframeAlpha = 1;
    wireframeRenderOrder = 10;
    wireframeSelectedColor = [1, 1, 1]; // #ffffff
    wireframeSelectedRenderOrder = 11;

    drawLineColor = [1, 0, 0]; // #ff0000
    drawLineHelperRenderOrder = 12;
    selectHelperColor = [1, 1, 1]; // #ffffff
    selectionPointColor = [1, 0, 0]; // #ff0000

    hiddenObjectOpacity = 0;
    edgeMode = 'threshold'; // 'hide' | 'show' | 'gradual' | 'threshold'
    edgeThresholdMultiplier = 1;

    get isDark() {
        return document.body.classList.contains('vscode-dark') ||
               document.body.classList.contains('vscode-high-contrast');
    }

    // Group colors — vivid for dark mode, toned down for light mode
    _meshGroupColors = [
        [0.902, 0.098, 0.294], // #e6194b
        [0.235, 0.706, 0.294], // #3cb44b
        [1,     0.882, 0.098], // #ffe119
        [0.941, 0.196, 0.902], // #f032e6
        [0.961, 0.510, 0.192], // #f58231
        [0.569, 0.118, 0.706], // #911eb4
        [0.275, 0.941, 0.941], // #46f0f0
        [0.737, 0.965, 0.047], // #bcf60c
        [0.980, 0.745, 0.745], // #fabebe
        [0,     0.502, 0.502], // #008080
        [0.902, 0.745, 1    ], // #e6beff
        [0.604, 0.388, 0.141], // #9a6324
        [0.263, 0.388, 0.847], // #4363d8
        [1,     0.980, 0.784], // #fffac8
        [0.502, 0,     0    ], // #800000
        [0.667, 1,     0.764], // #aaffc3
        [0.502, 0.502, 0    ], // #808000
        [1,     0.847, 0.694], // #ffd8b1
        [0,     0,     0.463], // #000075
        [0.502, 0.502, 0.502], // #808080
    ];

    get meshGroupColors() {
        if (this.isDark) return this._meshGroupColors;
        return this._meshGroupColors.map(([r, g, b]) => [r * 0.72, g * 0.72, b * 0.72]);
    }

    getColorForGroup() {
        const idx = this.grpIndex % this._meshGroupColors.length;
        this.grpIndex++;
        return this.meshGroupColors[idx];
    }

    // Object base colors — muted for light mode, vivid for dark mode
    _objectColorsLight = [
        [0.400, 0.620, 0.820], // steel blue
        [0.280, 0.700, 0.580], // teal
        [0.880, 0.560, 0.280], // amber
        [0.600, 0.400, 0.800], // lavender
        [0.380, 0.720, 0.420], // sage green
        [0.820, 0.380, 0.440], // rose
        [0.380, 0.680, 0.820], // sky
        [0.820, 0.620, 0.380], // bronze
    ];

    _objectColorsDark = [
        [0.440, 0.720, 0.980], // bright steel blue
        [0.240, 0.880, 0.700], // bright teal
        [0.980, 0.660, 0.320], // bright amber
        [0.720, 0.500, 0.980], // bright lavender
        [0.400, 0.900, 0.500], // bright sage green
        [0.980, 0.420, 0.520], // bright rose
        [0.360, 0.800, 0.980], // bright sky
        [0.980, 0.740, 0.440], // bright bronze
    ];

    get objectColors() {
        return this.isDark ? this._objectColorsDark : this._objectColorsLight;
    }

    getColorForObject() {
        const idx = this.objIndex % this.objectColors.length;
        this.objIndex++;
        return this.objectColors[idx];
    }
}
