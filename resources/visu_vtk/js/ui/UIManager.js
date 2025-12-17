/**
 * Manages the creation and interaction of UI elements in the visualization panel.
 */
class UIManager {
  /**
   * Manage a singleton instance
   */
  static get Instance() {
    if (!this._i) {
      this._i = new UIManager();
    }
    return this._i;
  }

  /**
   * Initializes the manager by adding onclick events, buttons and setting up the popup.
   * @param {Map <string, { faces: [], nodes: [] }} objects A map of objects with their corresponding face and node groups.
   */
  init(objects) {
    this.addOnClickEvents();
    this.addGroupButtons(objects);
    this.initGroupButtonsPopup(objects);
  }

  /**
   * Adds an onClick event for each of the pre-rendered buttons.
   */
  addOnClickEvents() {
    // Reset all groups highlight status
    const clearBtn = document.getElementById("clearBtn");
    clearBtn.addEventListener("click", () => {
      VisibilityManager.Instance.clear();
    });

    // Group buttons popup
    const selectGroupsBtn = document.getElementById("selectGroupsBtn");
    selectGroupsBtn.addEventListener("click", () => {
      this.openGroupButtonsPopup();
    });
    const saveBtn = document.getElementById("saveBtn");
    saveBtn.addEventListener("click", this.saveGroupButtonsPopup);
    const cancelBtn = document.getElementById("cancelBtn");
    cancelBtn.addEventListener("click", this.cancelGroupButtonsPopup);

    // Camera axis buttons, to allow quick camera control
    const xBtn = document.getElementById("xBtn");
    const yBtn = document.getElementById("yBtn");
    const zBtn = document.getElementById("zBtn");
    xBtn.addEventListener("click", () => {
      CameraManager.Instance.setCameraAxis("x");
    });
    yBtn.addEventListener("click", () => {
      CameraManager.Instance.setCameraAxis("y");
    });
    zBtn.addEventListener("click", () => {
      CameraManager.Instance.setCameraAxis("z");
    });

    // Help popup
    const helpBtn = document.getElementById("helpBtn");
    helpBtn.addEventListener("click", () => {
      this.openHelpPopup();
    });
    const closeHelpBtn = document.getElementById("closeHelpBtn");
    closeHelpBtn.addEventListener("click", () => {
      this.closeHelpPopup();
    });
  }

  /**
   * Add the list of group buttons to the sidebar.
   * @param {Map <string, { faces: [], nodes: [] }>} objects A map of objects with their corresponding face and node groups.
   */
  addGroupButtons(objects) {
    // Hack to retrieve necessary icons
    const objectIconUrl = document.getElementById("object").src;
    const faceIconUrl = document.getElementById("face").src;
    const nodeIconUrl = document.getElementById("node").src;

    // Get group buttons div
    const groupButtonsDiv = document.getElementById("groupButtons");

    // Add buttons for each object and its groups
    for (const object in objects) {
      const { faces, nodes } = objects[object];
      const objectName = object.replace("all_", "").replace(".obj", "");

      // Create object label
      const objectLabel = document.createElement("span");
      objectLabel.id = `obj_${objectName}`;
      objectLabel.classList.add(
        "relative",
        "h-4.5",
        "w-full",
        "flex",
        "justify-center",
        "items-center",
        "mb-2",
        "not-nth-of-type-[1]:mt-1",
        "text-xs",
        "text-black/70",
        "font-bold"
      );

      const icon = `<img src="${objectIconUrl}" class="size-4.5 absolute left-1.25 top-[0.5px]">`;
      const text = `<span class="pl-5">${objectName}</span>`;
      objectLabel.innerHTML = icon + text;

      groupButtonsDiv.appendChild(objectLabel);

      // Create group buttons for the current object
      const groups = faces.concat(nodes);
      groups.forEach((groupName) => {
        const btn = document.createElement("button");
        btn.id = `btn_${groupName}`;
        btn.classList.add(
          "relative",
          "flex",
          "items-center",
          "justify-center",
          "hover:bg-white/50",
          "rounded-sm",
          "bg-white/30",
          "text-black/70",
          "text-xs",
          "px-2",
          "pt-0.75",
          "pb-1.25",
          "w-full",
          "cursor-pointer"
        );

        const icon = `<img src="${
          faces.includes(groupName) ? faceIconUrl : nodeIconUrl
        }" class="size-4 absolute left-1.5 top-1">`;
        const text = `<span class="pl-5">${groupName}</span>`;
        btn.innerHTML = icon + text;

        btn.addEventListener("click", () => {
          VisibilityManager.Instance.setVisibility(groupName);
        });

        groupButtonsDiv.appendChild(btn);
      });
    }
  }

  /**
   * Set a group button's status between highlighted or not.
   * A highlighted button will be colorful with bold text, while a non highlighted button will be grey.
   * @param {HTMLButtonElement} groupName The group button that will be highlighted or not.
   * @param {number[]} color An RGB color array corresponding to the group. The highlight will be removed if not set.
   */
  highlightButton(groupName, color) {
    const btn = document.getElementById(`btn_${groupName}`);

    if (color) {
      // If the button was not highlighted, highlight it
      btn.classList.add("font-semibold", "hover:brightness-90");
      btn.classList.remove("bg-white/30");
      btn.style.backgroundColor = `rgb(${color[0] * 255}, ${color[1] * 255}, ${
        color[2] * 255
      }, 0.8)`;
    } else {
      // Else unapply the highlight
      btn.classList.remove("font-semibold", "hover:brightness-90");
      btn.classList.add("bg-white/30");
      btn.style.backgroundColor = "";
    }
  }

  /**
   * Add the list of group buttons to the sidebar.
   * @param {Map <string, { faces: [], nodes: [] }>} objects A map of objects with their corresponding face and node groups.
   */
  initGroupButtonsPopup(objects) {
    // Get group list inside the popup
    const groupList = document.getElementById("groupList");
    // Add buttons for each object and its groups
    for (const object in objects) {
      const { faces, nodes } = objects[object];
      const objectName = object.replace("all_", "").replace(".obj", "");

      // Create object div
      const objectDiv = document.createElement("div");
      objectDiv.classList.add("flex", "flex-col", "space-y-1", "mb-4");

      // Create object label
      const objectLabel = `<span class="font-semibold text-sm">${objectName}</span>`;
      objectDiv.innerHTML += objectLabel;

      // Create group checkboxes for the current object
      const groups = faces.concat(nodes);
      groups.forEach((groupName) => {
        const label = `<label class="flex items-center space-x-1 cursor-pointer select-none">
                <input class="mt-0.5" type="checkbox" checked />
                <span class="text-xs"> ${groupName} </span>
              </label>`;
        objectDiv.innerHTML += label;
      });
      groupList.append(objectDiv);
    }
  }

  /**
   * Open the group buttons popup
   */
  openGroupButtonsPopup() {
    const popup = document.getElementById("popup");
    const groupButtonsPopup = document.getElementById("groupButtonsPopup");
    popup.classList.remove("hidden!");
    groupButtonsPopup.classList.remove("hidden!");
  }

  /**
   * Save group visibility in the sidebar. All checked groups will be visible, while unchecked groups will be hidden.
   * If all the groups from an object are hidden, the object is also hidden from the sidebar.
   * Hidden groups are still visible on the 3D view, they are just hidden from the sidebar.
   */
  saveGroupButtonsPopup() {
    const groupList = document.getElementById("groupList");

    // Parse all objects
    for (let i = 0; i < groupList.children.length; ++i) {
      const objectDiv = groupList.children.item(i);

      // Retrieve current object name
      const objectNameSpan = objectDiv.querySelector("span.font-semibold");
      const objectName = objectNameSpan.textContent.trim();
      let allGroupsHidden = true;

      // Parse all labels for the current object
      const labels = objectDiv.querySelectorAll("label");
      labels.forEach((label) => {
        const input = label.querySelector("input");
        const span = label.querySelector("span");

        // Retrieve group name
        const groupName = span.textContent.trim();

        // Hide or show group in the sidebar
        const btn = document.getElementById(`btn_${groupName}`);
        if (input.checked) {
          btn.classList.remove("hidden!");
          allGroupsHidden = false;
        } else {
          btn.classList.add("hidden!");
        }
      });

      // Retrieve object label from the sidebar
      const objectLabel = document.getElementById(`obj_${objectName}`);
      if (allGroupsHidden) {
        objectLabel.classList.add("hidden!");
      } else {
        objectLabel.classList.remove("hidden!");
      }
    }

    // Close popup
    const popup = document.getElementById("popup");
    const groupButtonsPopup = document.getElementById("groupButtonsPopup");
    popup.classList.add("hidden!");
    groupButtonsPopup.classList.add("hidden!");
  }

  /**
   * Cancel the popup actions.
   * Checked status will be reset to what they were before opening, and no additional buttons will be shown or hidden.
   */
  cancelGroupButtonsPopup() {
    const groupList = document.getElementById("groupList");

    // Reset checked status for each group to what they were before opening the popup
    for (let i = 0; i < groupList.children.length; ++i) {
      const objectDiv = groupList.children.item(i);
      const labels = objectDiv.querySelectorAll("label");

      labels.forEach((label) => {
        const input = label.querySelector("input");
        const span = label.querySelector("span");

        // Retrieve group name
        const groupName = span.textContent.trim();

        // Set the checkbox state based on the button's visibility, since it did not change
        const btn = document.getElementById(`btn_${groupName}`);
        input.checked = !btn.classList.contains("hidden!");
      });
    }

    // Close popup
    const popup = document.getElementById("popup");
    const groupButtonsPopup = document.getElementById("groupButtonsPopup");
    popup.classList.add("hidden!");
    groupButtonsPopup.classList.add("hidden!");
  }

  /**
   * Open the help popup
   */
  openHelpPopup() {
    const popup = document.getElementById("popup");
    const helpPopup = document.getElementById("helpPopup");
    popup.classList.remove("hidden!");
    helpPopup.classList.remove("hidden!");
  }

  /**
   * Close the help popup
   */
  closeHelpPopup() {
    const popup = document.getElementById("popup");
    const helpPopup = document.getElementById("helpPopup");
    popup.classList.add("hidden!");
    helpPopup.classList.add("hidden!");
  }
}
