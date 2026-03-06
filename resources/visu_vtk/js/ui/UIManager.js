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
    const closeGroupsBtn = document.getElementById("closeGroupsBtn");
    closeGroupsBtn.addEventListener("click", () => {
      this.closeGroupButtonsPopup();
    });
    const resetGroupsBtn = document.getElementById("resetGroupsBtn");
    resetGroupsBtn.addEventListener("click", () => {
      this.resetGroupButtonsPopup();
    });

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

    // Settings popup
    const settingsBtn = document.getElementById("settingsBtn");
    settingsBtn.addEventListener("click", () => {
      this.openSettingsPopup();
    });
    const closeSettingsBtn = document.getElementById("closeSettingsBtn");
    closeSettingsBtn.addEventListener("click", () => {
      this.closeSettingsPopup();
    });
    const resetSettingsBtn = document.getElementById("resetSettingsBtn");
    resetSettingsBtn.addEventListener("click", () => {
      this.resetSettings();
    });

    // Hidden object opacity slider
    const hiddenOpacitySlider = document.getElementById("hiddenOpacitySlider");
    const hiddenOpacityValue = document.getElementById("hiddenOpacityValue");
    hiddenOpacitySlider.addEventListener("input", () => {
      const raw = parseInt(hiddenOpacitySlider.value, 10);
      const pct = Math.min(raw, 50);
      hiddenOpacitySlider.value = pct;
      hiddenOpacityValue.textContent = `${pct}%`;
      GlobalSettings.Instance.hiddenObjectOpacity = pct / 100;
      VisibilityManager.Instance.applyHiddenObjectOpacity();
      Controller.Instance.getVSCodeAPI().postMessage({
        type: "saveSettings",
        settings: { hiddenObjectOpacity: GlobalSettings.Instance.hiddenObjectOpacity },
      });
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
      const text = `<span id="objName_${object}" class="flex-1 truncate text-center px-2 cursor-pointer select-none">${objectName}</span>`;
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

      // Name span toggles group container visibility (disabled when all groups are hidden)
      document.getElementById(`objName_${object}`).addEventListener("click", () => {
        const grpHidden = document.getElementById(`grpHidden_${object}`);
        const allHidden = grpHidden && !grpHidden.classList.contains("hidden!") &&
          [...groupContainer.querySelectorAll(`[id^="btn_${object}::"]`)].every(b => b.classList.contains("hidden!"));
        if (allHidden) { return; }
        const collapsed = groupContainer.classList.toggle("hidden!");
        groupCountEl.classList.toggle("hidden!", !collapsed);
      });

      // Create group buttons for the current object
      const groupNames = faces.concat(nodes);
      groupNames.forEach((groupName) => {
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

      // Small label showing how many groups are hidden from the sidebar
      const grpHiddenEl = document.createElement("div");
      grpHiddenEl.id = `grpHidden_${object}`;
      grpHiddenEl.classList.add("hidden!", "w-full", "text-center", "text-[0.7rem]", "pb-1");
      grpHiddenEl.style.color = "var(--ui-text-muted)";
      groupContainer.appendChild(grpHiddenEl);

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
      btn.classList.add("font-semibold");
      btn.dataset.highlighted = "1";
      btn.style.background = `rgb(${color[0] * 255}, ${color[1] * 255}, ${color[2] * 255}, 0.8)`;
      btn.style.color = "var(--ui-highlight-text)";
    } else {
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
    const groupList = document.getElementById("groupList");

    const faceSvgPath = "M161-366q-16-12-15.5-31.5T162-429q11-8 24-8t24 8l270 209 270-209q11-8 24-8t24 8q16 12 16.5 31.5T799-366L529-156q-22 17-49 17t-49-17L161-366Zm270 8L201-537q-31-24-31-63t31-63l230-179q22-17 49-17t49 17l230 179q31 24 31 63t-31 63L529-358q-22 17-49 17t-49-17Zm49-64 230-178-230-178-230 178 230 178Zm0-178Z";
    const nodeSvgPath = "M580-120q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T620-240q0-17-11.5-28.5T580-280q-17 0-28.5 11.5T540-240q0 17 11.5 28.5T580-200Zm80-200q-92 0-156-64t-64-156q0-92 64-156t156-64q92 0 156 64t64 156q0 92-64 156t-156 64Zm0-80q59 0 99.5-40.5T800-620q0-59-40.5-99.5T660-760q-59 0-99.5 40.5T520-620q0 59 40.5 99.5T660-480ZM280-240q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47Zm0-80q33 0 56.5-23.5T360-400q0-33-23.5-56.5T280-480q-33 0-56.5 23.5T200-400q0 33 23.5 56.5T280-320Zm300 80Zm80-380ZM280-400Z";
    const objSvgPath = "M440-183v-274L200-596v274l240 139Zm80 0 240-139v-274L520-457v274Zm-40-343 237-137-237-137-237 137 237 137ZM160-252q-19-11-29.5-29T120-321v-318q0-22 10.5-40t29.5-29l280-161q19-11 40-11t40 11l280 161q19 11 29.5 29t10.5 40v318q0 22-10.5 40T800-252L520-91q-19 11-40 11t-40-11L160-252Zm320-228Z";
    const makeSvg = (path, fill, cls) => {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("viewBox", "0 -960 960 960");
      svg.setAttribute("fill", fill);
      svg.classList.add(...cls.split(" "));
      const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      p.setAttribute("d", path);
      svg.appendChild(p);
      return svg;
    };

    for (const object in objects) {
      const { faces, nodes } = objects[object];
      const objectName = object.replace("all_", "").replace(".obj", "");

      const [r, g, b] = objects[object].color ?? [0.537, 0.529, 0.529];
      const colorCss = `rgb(${Math.round(r * 255)},${Math.round(g * 255)},${Math.round(b * 255)})`;

      const objectDiv = document.createElement("div");
      objectDiv.classList.add("break-inside-avoid", "flex", "flex-col", "space-y-1.5", "mb-5");
      objectDiv.dataset.object = object;

      // Object header with select-all toggle
      const header = document.createElement("div");
      header.classList.add("flex", "items-center", "justify-between", "pb-1");
      header.style.borderBottom = "1px solid var(--ui-border)";

      const nameGroup = document.createElement("div");
      nameGroup.classList.add("flex", "items-center", "gap-1.5");
      nameGroup.appendChild(makeSvg(objSvgPath, colorCss, "size-4 shrink-0"));

      const nameSpan = document.createElement("span");
      nameSpan.classList.add("font-semibold", "text-sm");
      nameSpan.textContent = objectName;
      nameGroup.appendChild(nameSpan);

      const toggleAll = document.createElement("button");
      toggleAll.classList.add("text-xs", "leading-none", "cursor-pointer", "px-1.5", "py-0.5", "rounded-sm");
      toggleAll.style.color = "var(--ui-text-secondary)";
      toggleAll.addEventListener("mouseover", () => { toggleAll.style.background = "var(--ui-element-bg)"; });
      toggleAll.addEventListener("mouseout", () => { toggleAll.style.background = ""; });
      toggleAll.textContent = "Hide all";

      header.appendChild(nameGroup);
      header.appendChild(toggleAll);
      objectDiv.appendChild(header);

      // Group checkboxes
      const groups = faces.concat(nodes);
      groups.forEach((groupName) => {
        const label = document.createElement("label");
        label.classList.add("flex", "items-center", "gap-1.5", "cursor-pointer", "select-none");

        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = true;
        input.classList.add("custom-cb");
        input.addEventListener("change", () => {
          this.applyGroupVisibility(object, objectDiv);
          toggleAll.textContent = this.allUnchecked(objectDiv) ? "Show all" : "Hide all";
        });

        const isFace = faces.includes(groupName);
        const groupIcon = makeSvg(isFace ? faceSvgPath : nodeSvgPath, "currentColor", "size-3.5 shrink-0");

        const span = document.createElement("span");
        span.classList.add("text-xs", "truncate", "-translate-y-px");
        span.textContent = groupName;

        label.appendChild(input);
        label.appendChild(groupIcon);
        label.appendChild(span);
        objectDiv.appendChild(label);
      });

      toggleAll.addEventListener("click", () => {
        const allOff = this.allUnchecked(objectDiv);
        objectDiv.querySelectorAll("input[type=checkbox]").forEach((cb) => { cb.checked = allOff; });
        this.applyGroupVisibility(object, objectDiv);
        toggleAll.textContent = allOff ? "Hide all" : "Show all";
      });

      groupList.appendChild(objectDiv);
    }
  }

  /**
   * Returns true if all checkboxes in the given object div are unchecked.
   * @param {HTMLElement} objectDiv
   */
  allUnchecked(objectDiv) {
    return [...objectDiv.querySelectorAll("input[type=checkbox]")].every((cb) => !cb.checked);
  }

  /**
   * Apply checkbox state to sidebar button visibility for one object.
   * @param {string} objectKey
   * @param {string} objectName
   * @param {HTMLElement} objectDiv
   */
  applyGroupVisibility(objectKey, objectDiv) {
    let hiddenCount = 0;
    objectDiv.querySelectorAll("label").forEach((label) => {
      const input = label.querySelector("input");
      const span = label.querySelector("span");
      const btn = document.getElementById(`btn_${objectKey}::${span.textContent.trim()}`);
      if (input.checked) {
        btn.classList.remove("hidden!");
      } else {
        btn.classList.add("hidden!");
        hiddenCount++;
      }
    });

    const grpHiddenEl = document.getElementById(`grpHidden_${objectKey}`);
    if (grpHiddenEl) {
      if (hiddenCount > 0) {
        grpHiddenEl.textContent = `${hiddenCount} hidden`;
        grpHiddenEl.classList.remove("hidden!");
      } else {
        grpHiddenEl.classList.add("hidden!");
      }
    }

    // Update name span cursor: not collapsible when all groups are hidden
    const allHidden = hiddenCount === objectDiv.querySelectorAll("label").length;
    const nameSpan = document.getElementById(`objName_${objectKey}`);
    if (nameSpan) {
      nameSpan.style.cursor = allHidden ? "default" : "";
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
   * Reset all group checkboxes to checked (show all groups in sidebar).
   */
  resetGroupButtonsPopup() {
    const groupList = document.getElementById("groupList");
    for (const objectDiv of groupList.children) {
      const objectKey = objectDiv.dataset.object;
      objectDiv.querySelectorAll("input[type=checkbox]").forEach((cb) => { cb.checked = true; });
      this.applyGroupVisibility(objectKey, objectDiv);
      const toggleAll = objectDiv.querySelector("button");
      if (toggleAll) { toggleAll.textContent = "Hide all"; }
    }
  }

  /**
   * Close the group buttons popup
   */
  closeGroupButtonsPopup() {
    const popup = document.getElementById("popup");
    const groupButtonsPopup = document.getElementById("groupButtonsPopup");
    popup.classList.add("hidden!");
    groupButtonsPopup.classList.add("hidden!");
  }

  /**
   * Reset all settings to their default values, apply them, and save them.
   */
  resetSettings() {
    this.applySettings({ hiddenObjectOpacity: 0 });
    VisibilityManager.Instance.applyHiddenObjectOpacity();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: "saveSettings",
      settings: { hiddenObjectOpacity: 0 },
    });
  }

  /**
   * Apply settings received from the extension to the UI and runtime state.
   * @param {Object} settings
   */
  applySettings(settings) {
    if (!settings) { return; }

    if (settings.hiddenObjectOpacity !== undefined) {
      const pct = Math.round(settings.hiddenObjectOpacity * 100);
      const slider = document.getElementById("hiddenOpacitySlider");
      const label = document.getElementById("hiddenOpacityValue");
      slider.value = pct;
      label.textContent = `${pct}%`;
      GlobalSettings.Instance.hiddenObjectOpacity = settings.hiddenObjectOpacity;
    }
  }

  /**
   * Open the settings popup
   */
  openSettingsPopup() {
    const popup = document.getElementById("popup");
    const settingsPopup = document.getElementById("settingsPopup");
    popup.classList.remove("hidden!");
    settingsPopup.classList.remove("hidden!");
  }

  /**
   * Close the settings popup
   */
  closeSettingsPopup() {
    const popup = document.getElementById("popup");
    const settingsPopup = document.getElementById("settingsPopup");
    popup.classList.add("hidden!");
    settingsPopup.classList.add("hidden!");
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
