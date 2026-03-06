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
    const eyeIconUrl = document.getElementById("eye").src;
    // Inline SVG paths for face/node icons (fill="currentColor" inherits button text color)
    const faceSvgPath = "M161-366q-16-12-15.5-31.5T162-429q11-8 24-8t24 8l270 209 270-209q11-8 24-8t24 8q16 12 16.5 31.5T799-366L529-156q-22 17-49 17t-49-17L161-366Zm270 8L201-537q-31-24-31-63t31-63l230-179q22-17 49-17t49 17l230 179q31 24 31 63t-31 63L529-358q-22 17-49 17t-49-17Zm49-64 230-178-230-178-230 178 230 178Zm0-178Z";
    const nodeSvgPath = "M580-120q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T620-240q0-17-11.5-28.5T580-280q-17 0-28.5 11.5T540-240q0 17 11.5 28.5T580-200Zm80-200q-92 0-156-64t-64-156q0-92 64-156t156-64q92 0 156 64t64 156q0 92-64 156t-156 64Zm0-80q59 0 99.5-40.5T800-620q0-59-40.5-99.5T660-760q-59 0-99.5 40.5T520-620q0 59 40.5 99.5T660-480ZM280-240q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47Zm0-80q33 0 56.5-23.5T360-400q0-33-23.5-56.5T280-480q-33 0-56.5 23.5T200-400q0 33 23.5 56.5T280-320Zm300 80Zm80-380ZM280-400Z";
    const eyeOffIconUrl = document.getElementById("eye_off").src;

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
        "h-4.5",
        "w-full",
        "self-stretch",
        "flex",
        "items-center",
        "gap-1",
        "pl-1.25",
        "pr-0.5",
        "mb-2",
        "not-nth-of-type-[1]:mt-1",
        "text-xs",
        "font-bold"
      );
      objectLabel.style.color = "var(--ui-text-primary)";

      const groupCount = faces.length + nodes.length;

      const [r, g, b] = objects[object].color ?? [0.537, 0.529, 0.529];
      const colorCss = `rgb(${Math.round(r * 255)},${Math.round(g * 255)},${Math.round(b * 255)})`;
      const objSvgPath = "M440-183v-274L200-596v274l240 139Zm80 0 240-139v-274L520-457v274Zm-40-343 237-137-237-137-237 137 237 137ZM160-252q-19-11-29.5-29T120-321v-318q0-22 10.5-40t29.5-29l280-161q19-11 40-11t40 11l280 161q19 11 29.5 29t10.5 40v318q0 22-10.5 40T800-252L520-91q-19 11-40 11t-40-11L160-252Zm320-228Z";
      const icon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" class="size-4.5 shrink-0 mt-0.5" fill="${colorCss}"><path d="${objSvgPath}"/></svg>`;
      const text = `<span id="objName_${object}" class="flex-1 truncate text-center px-2 cursor-pointer">${objectName}</span>`;
      const eyeBtn = `<button id="eyeBtn_${object}" title="Hide/show mesh" class="size-4.5 shrink-0 flex items-center justify-center cursor-pointer opacity-40 hover:opacity-90"><img id="eyeIcon_${object}" src="${eyeIconUrl}" class="size-4 block mt-0.5" style="filter: var(--icon-filter)"></button>`;
      objectLabel.innerHTML = icon + text + eyeBtn;

      groupButtonsDiv.appendChild(objectLabel);

      // Eye button toggles full mesh visibility
      document.getElementById(`eyeBtn_${object}`).addEventListener("click", () => {
        const nowVisible = VisibilityManager.Instance.toggleObjectVisibility(object);
        document.getElementById(`eyeIcon_${object}`).src = nowVisible ? eyeIconUrl : eyeOffIconUrl;
      });

      // Create collapsible container for group buttons
      const groupContainer = document.createElement("div");
      groupContainer.id = `grpContainer_${object}`;
      groupContainer.classList.add("w-full", "flex", "flex-col", "items-center", "space-y-1");

      // Create collapsed summary shown in place of the buttons
      const groupCountEl = document.createElement("div");
      groupCountEl.id = `grpCount_${object}`;
      groupCountEl.classList.add("hidden!", "w-full", "text-center", "text-[0.7rem]", "font-normal", "mb-2");
      groupCountEl.style.color = "var(--ui-text-muted)";
      groupCountEl.textContent = `${groupCount} groups`;

      // Name span toggles group container visibility
      document.getElementById(`objName_${object}`).addEventListener("click", () => {
        const collapsed = groupContainer.classList.toggle("hidden!");
        groupCountEl.classList.toggle("hidden!", !collapsed);
      });

      // Create group buttons for the current object
      const groups = faces.concat(nodes);
      groups.forEach((groupName) => {
        const btn = document.createElement("button");
        btn.id = `btn_${object}::${groupName}`;
        btn.classList.add(
          "relative",
          "flex",
          "items-center",
          "justify-center",
          "rounded-sm",
          "text-xs",
          "px-2",
          "pt-0.75",
          "pb-1.25",
          "w-full",
          "cursor-pointer"
        );
        btn.style.background = "var(--ui-element-bg)";
        btn.style.color = "var(--ui-text-primary)";
        btn.addEventListener("mouseover", () => {
          if (!btn.dataset.highlighted) {
            btn.style.background = "var(--ui-element-bg-hover)";
          }
        });
        btn.addEventListener("mouseout", () => {
          if (!btn.dataset.highlighted) {
            btn.style.background = "var(--ui-element-bg)";
          }
        });

        const icon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" class="size-4 absolute left-1.5 top-1" fill="currentColor"><path d="${faces.includes(groupName) ? faceSvgPath : nodeSvgPath}"/></svg>`;
        const text = `<span class="pl-5">${groupName}</span>`;
        btn.innerHTML = icon + text;

        btn.addEventListener("click", () => {
          VisibilityManager.Instance.setVisibility(`${object}::${groupName}`);
        });

        groupContainer.appendChild(btn);
      });

      groupButtonsDiv.appendChild(groupContainer);
      groupButtonsDiv.appendChild(groupCountEl);
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
      btn.classList.add("font-semibold");
      btn.dataset.highlighted = "1";
      btn.style.background = `rgb(${color[0] * 255}, ${color[1] * 255}, ${color[2] * 255}, 0.8)`;
      btn.style.color = "var(--ui-highlight-text)";
    } else {
      // Else unapply the highlight
      btn.classList.remove("font-semibold");
      delete btn.dataset.highlighted;
      btn.style.background = "var(--ui-element-bg)";
      btn.style.color = "var(--ui-text-primary)";
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
      objectDiv.dataset.object = object;

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

      // Retrieve current object name and key
      const objectNameSpan = objectDiv.querySelector("span.font-semibold");
      const objectName = objectNameSpan.textContent.trim();
      const objectKey = objectDiv.dataset.object;
      let allGroupsHidden = true;

      // Parse all labels for the current object
      const labels = objectDiv.querySelectorAll("label");
      labels.forEach((label) => {
        const input = label.querySelector("input");
        const span = label.querySelector("span");

        // Retrieve group name
        const groupName = span.textContent.trim();

        // Hide or show group in the sidebar
        const btn = document.getElementById(`btn_${objectKey}::${groupName}`);
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

      const objectKey = objectDiv.dataset.object;
      labels.forEach((label) => {
        const input = label.querySelector("input");
        const span = label.querySelector("span");

        // Retrieve group name
        const groupName = span.textContent.trim();

        // Set the checkbox state based on the button's visibility, since it did not change
        const btn = document.getElementById(`btn_${objectKey}::${groupName}`);
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
