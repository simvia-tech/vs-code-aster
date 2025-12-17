/**
 * Manages visibility of groups in the visualization module.
 */
class VisibilityManager {
  /**
   * Manage a singleton instance
   */
  static get Instance() {
    if (!this._i) {
      this._i = new VisibilityManager();
    }
    return this._i;
  }

  /**
   * Initializes the manager with groups and their hierarchy.
   * @param {Map <string, Group>} groups A map of group names to group objects.
   * @param {Map <string, { faces: [], nodes: [] }>} objects A map of objects with their corresponding face and node groups.
   */
  init(groups, objects) {
    this.groups = groups;
    this.visibleGroupsByObject = {};

    for (const object in objects) {
      this.visibleGroupsByObject[object] = 0;
    }
  }

  /**
   * Sets visibility for a given group and updates associated object transparency.
   * @param {string} groupName Name of the group to modify.
   * @param {boolean} visible Optional visibility state; toggles if omitted.
   * @returns {Object} Current visibility info: {visible, color, isFaceGroup}
   */
  setVisibility(groupName, visible) {
    // Helper function to send messages to the backend
    const post = (text) => {
      Controller.Instance.getVSCodeAPI().postMessage({
        type: "debugPanel",
        text,
      });
    };

    // Handle errors
    const group = this.groups[groupName];
    if (!group) {
      post(`setVisibility: group "${groupName}" has no group defined`);
      return;
    }
    const object = group.fileGroup;
    if (!object) {
      post(`setVisibility: group "${groupName}" has no parent object`);
      return;
    }
    const actor = group.actor;
    if (!actor) {
      post(`setVisibility: no actor found for group "${groupName}"`);
      return;
    }

    // Get data about the group
    const color = group.getColor();
    const isFaceGroup = group.isFaceGroup;

    // Store the previous visibility state before changing it
    const wasVisible = actor.getVisibility();

    if (typeof visible === "boolean") {
      // If 'visible' is set, set the new visibility accordingly
      actor.setVisibility(visible);
    } else {
      // Else, toggle visibility
      actor.setVisibility(!actor.getVisibility());
    }

    // Make the whole object transparent (except from the selected groups) if at least one group is selected
    // Or make it opaque if no groups are selected
    const isVisible = actor.getVisibility();

    // Only update the counter if visibility actually changed
    if (wasVisible !== isVisible) {
      const visibleGroupsCount = this.visibleGroupsByObject[object];
      if (
        (visibleGroupsCount === 0 && isVisible) ||
        (visibleGroupsCount === 1 && !isVisible)
      ) {
        this.setTransparence(isVisible, object);
      }
      this.visibleGroupsByObject[object] += isVisible ? 1 : -1;
    }

    // Change group button highlight status
    if (isVisible) {
      UIManager.Instance.highlightButton(groupName, color);
    } else {
      UIManager.Instance.highlightButton(groupName);
    }

    // Re-render the VTK window
    VtkApp.Instance.getRenderWindow().render();

    return { visible: isVisible, color, isFaceGroup }; // Unused, is this really necessary ?
  }

  /**
   * Sets the opacity of an object.
   * @param {boolean} transparent Whether the object should be partially transparent or opaque.
   * @param {string} object Name of the object.
   */
  setTransparence(transparent, object) {
    if (!this.groups) {
      return;
    }
    const meshOpacity = transparent ? 0.2 : 1;
    const group = this.groups[object];
    group.setOpacity(meshOpacity);
  }

  /**
   * Resets visibility and transparency for all groups.
   */
  clear() {
    /**
     * Parse all groups and set their visibility to false (meaning they are not highlighted)
     */
    for (const [groupName, group] of Object.entries(this.groups)) {
      if (!group.actor) {
        continue;
      }
      if (groupName.includes("all_")) {
        continue;
      }
      group.setVisibility(false);

      // Change group button highlight status
      UIManager.Instance.highlightButton(groupName);
    }

    // Make all objects opaque
    for (const object in this.visibleGroupsByObject) {
      this.setTransparence(false, object);
      this.visibleGroupsByObject[object] = 0;
    }

    // Re-render
    VtkApp.Instance.getRenderWindow().render();
  }
}
