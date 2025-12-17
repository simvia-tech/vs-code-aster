/**
 * Controller for managing rendering operations and group visibility in the visualization module.
 */
class Controller {
  static get Instance() {
    if (!this._i) {
      this._i = new Controller();
    }
    return this._i;
  }

  /**
   * Initializes the render controller with the given scene and VS Code API entry.
   * @param {HTMLElement} scene - The HTML scene for 3D rendering.
   * @param {any} vsCodeApiEntry - The VS Code API entry point.
   */
  init(scene, vsCodeApiEntry) {
    this._scene = scene;
    this._vsCodeApi = vsCodeApiEntry;
    VtkApp.Instance.init(scene);
  }

  getScene() {
    return this._scene;
  }

  getVSCodeAPI() {
    return this._vsCodeApi;
  }

  /**
   * Loads a file and updates the group list in the VS Code webview.
   * @param {string[]} fileContexts - The contexts of the files to load.
   * @param {string[]} fileNames - The names of the files to load.
   */
  loadFiles(fileContexts, fileNames) {
    const lfr = new CreateGroups(fileContexts, fileNames);
    lfr.do();
    this.initManagers();
    this.getVSCodeAPI().postMessage({
      type: "groups",
      groupList: this.getGroupNames(),
    });
  }

  saveGroups(groups, groupHierarchy) {
    this._groups = groups;
    this._groupHierarchy = groupHierarchy;
    Controller.Instance.getVSCodeAPI().postMessage({
      type: "debugPanel",
      text: `Actors and hierarchy saved`,
    });
  }

  initManagers() {
    UIManager.Instance.init(this._groupHierarchy);
    VisibilityManager.Instance.init(this._groups, this._groupHierarchy);
    CameraManager.Instance.init(this._groups);
  }

  getGroupNames() {
    if (!this._groups) {
      return [];
    }
    return Object.keys(this._groups).filter((key) => !key.includes("all_"));
  }
}
