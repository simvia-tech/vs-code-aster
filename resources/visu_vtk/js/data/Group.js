/**
 * Represents a group in the visualization module.
 * Can be a fileGroup or a sub-group of faces/nodes.
 */
class Group {
    /**
     * @param {vtkActor} actor - The VTK actor associated with the group
     * @param {string} name - Name of the group (fileGroup or sub-group)
     * @param {boolean} isFaceGroup - True for face group, false for nodal
     * @param {string|null} fileGroup - Parent fileGroup name (null if this is a fileGroup)
     * @param {number|null} parentSize - Size of the parent fileGroup (null if this is a fileGroup)
     */
    constructor(actor, name, isFaceGroup, fileGroup = null, parentSize = null, colorIndex = null, isObjectActor = false, cellCount = null) {
        this.actor = actor;
        this.name = name;
        this.isFaceGroup = isFaceGroup;
        this.fileGroup = fileGroup;
        this.size = parentSize;
        this.colorIndex = colorIndex;
        this.isObjectActor = isObjectActor;
        this.cellCount = cellCount;
    }

    applyThemeColor() {
        if (this.colorIndex === null) return;
        const colors = this.isObjectActor
            ? GlobalSettings.Instance.objectColors
            : GlobalSettings.Instance.meshGroupColors;
        const color = colors[this.colorIndex % colors.length];
        this.actor.getProperty().setColor(color);
        this._applyEdgeColor();
    }

    /**
     * Updates edge rendering based on the current edge mode and zoom level.
     * @param {number} currentDistance
     * @param {number} initialDistance
     */
    updateEdgeVisibility(currentDistance, initialDistance) {
        if (this.cellCount === null) return;
        const prop = this.actor.getProperty();
        const mode = GlobalSettings.Instance.edgeMode;

        if (mode === 'hide') {
            prop.setEdgeVisibility(false);
            return;
        }
        if (mode === 'show') {
            prop.setEdgeVisibility(true);
            prop.setEdgeColor(0, 0, 0);
            return;
        }

        const threshold = initialDistance * Math.sqrt(15000 / this.cellCount) * GlobalSettings.Instance.edgeThresholdMultiplier;

        if (mode === 'threshold') {
            prop.setEdgeVisibility(currentDistance < threshold);
            prop.setEdgeColor(0, 0, 0);
            return;
        }

        // 'gradual': blend edge color from surface color (invisible) to black (fully visible)
        prop.setEdgeVisibility(true);
        this._edgeT = Math.min(1, Math.max(0, threshold / currentDistance));
        this._applyEdgeColor();
    }

    _applyEdgeColor() {
        const t = this._edgeT ?? 0;
        const [r, g, b] = this.actor.getProperty().getColor();
        this.actor.getProperty().setEdgeColor(r * (1 - t), g * (1 - t), b * (1 - t));
    }

    /**
     * Sets the visual point size of the actor based on distance.
     * @param {number} distance - Distance used to compute scaling
     */
    setSize(distance) {
        const decay = this.size / 5;
        const scale = Math.max(30 * (1 / Math.sqrt(1 + distance / decay)), 0);
        this.actor.getProperty().setPointSize(scale);
    }

    getColor() {
        return this.actor.getProperty().getColor();
    }

    setVisibility(visible) {
        this.actor.setVisibility(visible);
    }

    setOpacity(opacity) {
        this.actor.getProperty().setOpacity(opacity);
    }
}
