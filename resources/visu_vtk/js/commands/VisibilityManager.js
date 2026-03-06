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
    this.hiddenObjects = {};
    this.highlightedGroups = new Set();

    for (const object in objects) {
      this.visibleGroupsByObject[object] = 0;
      this.hiddenObjects[object] = false;
    }
  }

  /**
   * Sets visibility for a given group and updates associated object transparency.
   * The highlighted state is tracked independently from actor visibility so that
   * hiding/showing an entire object does not corrupt the highlight state.
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

    // Determine new highlighted state from the tracking set, not from actor visibility.
    // This ensures correctness even when the whole object is hidden.
    const wasHighlighted = this.highlightedGroups.has(groupName);
    const isHighlighted =
      typeof visible === "boolean" ? visible : !wasHighlighted;

    // Update the highlighted tracking set
    if (isHighlighted) {
      this.highlightedGroups.add(groupName);
    } else {
      this.highlightedGroups.delete(groupName);
    }

    // Apply to actor only if the parent object is not globally hidden
    if (!this.hiddenObjects[object]) {
      group.setVisibility(isHighlighted);
    }

    // Update transparency counter when highlight state actually changes
    if (wasHighlighted !== isHighlighted) {
      const visibleGroupsCount = this.visibleGroupsByObject[object];
      if (!this.hiddenObjects[object]) {
        if (
          (visibleGroupsCount === 0 && isHighlighted) ||
          (visibleGroupsCount === 1 && !isHighlighted)
        ) {
          this.setTransparence(isHighlighted, object);
        }
      }
      this.visibleGroupsByObject[object] += isHighlighted ? 1 : -1;
    }

    // Change group button highlight status
    if (isHighlighted) {
      UIManager.Instance.highlightButton(groupName, color);
    } else {
      UIManager.Instance.highlightButton(groupName);
    }

    // Re-render the VTK window
    VtkApp.Instance.getRenderWindow().render();

    return { visible: isHighlighted, color, isFaceGroup };
  }

  /**
   * Toggles the visibility of an entire object (mesh).
   * When hidden, all actors for the object are invisible.
   * When shown, the file group and any highlighted sub-groups are restored.
   * @param {string} object Name of the file group (e.g. "all_mesh.obj").
   * @returns {boolean} True if the object is now visible, false if now hidden.
   */
  toggleObjectVisibility(object) {
    // Toggle hidden state
    const nowVisible = this.hiddenObjects[object]; // was hidden → now visible
    this.hiddenObjects[object] = !nowVisible;

    // Show/hide the file group actor (the full mesh)
    const fileGroup = this.groups[object];
    if (fileGroup) {
      if (nowVisible) {
        // Showing: restore visibility and the correct opacity
        fileGroup.actor.setVisibility(true);
        const opacity = this.visibleGroupsByObject[object] > 0 ? 0.2 : 1.0;
        fileGroup.setOpacity(opacity);
      } else {
        // Hiding: use ghost opacity (may be 0 for fully invisible)
        const hiddenOpacity = GlobalSettings.Instance.hiddenObjectOpacity;
        if (hiddenOpacity === 0) {
          fileGroup.actor.setVisibility(false);
        } else {
          fileGroup.actor.setVisibility(true);
          fileGroup.setOpacity(hiddenOpacity);
        }
      }
    }

    // Show/hide sub-group actors based on their highlighted state
    for (const [groupName, group] of Object.entries(this.groups)) {
      if (group.fileGroup === object) {
        group.actor.setVisibility(
          nowVisible && this.highlightedGroups.has(groupName)
        );
      }
    }

    VtkApp.Instance.getRenderWindow().render();
    return nowVisible;
  }

  /**
   * Sets the opacity of an object.
   * @param {boolean} transparent Whether the object should be partially transparent or opaque.
   * @param {string} object Name of the object.
   */
  setTransparence(transparent, object) {
    if (!this.groups || this.hiddenObjects[object]) {
      return;
    }
    const meshOpacity = transparent ? 0.2 : 1;
    const group = this.groups[object];
    group.setOpacity(meshOpacity);
  }

  /**
   * Re-applies the current hiddenObjectOpacity to all hidden objects.
   * Called when the opacity slider value changes.
   */
  applyHiddenObjectOpacity() {
    const hiddenOpacity = GlobalSettings.Instance.hiddenObjectOpacity;
    for (const object in this.hiddenObjects) {
      if (!this.hiddenObjects[object]) continue;
      const fileGroup = this.groups[object];
      if (!fileGroup) continue;
      if (hiddenOpacity === 0) {
        fileGroup.actor.setVisibility(false);
      } else {
        fileGroup.actor.setVisibility(true);
        fileGroup.setOpacity(hiddenOpacity);
      }
    }
    VtkApp.Instance.getRenderWindow().render();
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
      if (group.fileGroup === null) {
        continue;
      }
      group.setVisibility(false);

      // Change group button highlight status
      UIManager.Instance.highlightButton(groupName);
    }

    // Reset highlighted tracking
    this.highlightedGroups.clear();

    // Make all visible objects opaque
    for (const object in this.visibleGroupsByObject) {
      this.setTransparence(false, object);
      this.visibleGroupsByObject[object] = 0;
    }

    // Re-render
    VtkApp.Instance.getRenderWindow().render();
  }
}
