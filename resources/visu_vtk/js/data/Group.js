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
    constructor(actor, name, isFaceGroup, fileGroup = null, parentSize = null) {
        this.actor = actor;             
        this.name = name;                  
        this.isFaceGroup = isFaceGroup;     
        this.fileGroup = fileGroup;
        this.size = parentSize;
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
