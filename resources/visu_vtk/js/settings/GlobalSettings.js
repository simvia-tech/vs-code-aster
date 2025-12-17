class GlobalSettings {
    static get Instance() {
        if (!this._instance) {
            this._instance = new GlobalSettings();
        }
        return this._instance;
    }

    constructor() {
        this.grpIndex = 0;
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

    // couleurs des groupes
    meshGroupColors = [
        [0.902, 0.098, 0.294], // #e6194b
        [0.235, 0.706, 0.294], // #3cb44b
        [1, 0.882, 0.098],     // #ffe119
        [0.941, 0.196, 0.902], // #f032e6
        [0.961, 0.510, 0.192], // #f58231
        [0.569, 0.118, 0.706], // #911eb4
        [0.275, 0.941, 0.941], // #46f0f0
        [0.737, 0.965, 0.047], // #bcf60c
        [0.980, 0.745, 0.745], // #fabebe
        [0, 0.502, 0.502],     // #008080
        [0.902, 0.745, 1],     // #e6beff
        [0.604, 0.388, 0.141], // #9a6324
        [0.263, 0.388, 0.847], // #4363d8
        [1, 0.980, 0.784],     // #fffac8
        [0.502, 0, 0],         // #800000
        [0.667, 1, 0.764],     // #aaffc3
        [0.502, 0.502, 0],     // #808000
        [1, 0.847, 0.694],     // #ffd8b1
        [0, 0, 0.463],         // #000075
        [0.502, 0.502, 0.502], // #808080
    ];

    getColorForGroup() {
        let idx = this.grpIndex % this.meshGroupColors.length;
        this.grpIndex++;
        return this.meshGroupColors[idx];
    }
}
