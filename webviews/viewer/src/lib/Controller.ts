import { VtkApp } from './core/VtkApp';
import { CreateGroups } from './data/CreateGroups';
import { VisibilityManager } from './commands/VisibilityManager';
import { CameraManager } from './interaction/CameraManager';
import { groupHierarchy as groupHierarchyStore, loadingProgress, loadingMessage } from './state';
import type { Group } from './data/Group';

export class Controller {
  private static _i: Controller;
  private _scene: HTMLElement | null = null;
  private _vsCodeApi: any = null;
  private _groups: Record<string, Group> | null = null;
  private _groupHierarchy: Record<string, any> | null = null;

  static get Instance(): Controller {
    if (!this._i) {
      this._i = new Controller();
    }
    return this._i;
  }

  init(scene: HTMLElement, vsCodeApiEntry: any): void {
    this._scene = scene;
    this._vsCodeApi = vsCodeApiEntry;
    VtkApp.Instance.init(scene);
  }

  getScene(): HTMLElement | null {
    return this._scene;
  }

  getVSCodeAPI(): any {
    return this._vsCodeApi;
  }

  async loadFiles(fileContexts: string[], fileNames: string[]): Promise<void> {
    if (this._groups) {
      return;
    }
    loadingProgress.set(0);
    loadingMessage.set('');
    const lfr = new CreateGroups(fileContexts, fileNames);
    await lfr.do(
      (progress) => loadingProgress.set(progress),
      (message) => loadingMessage.set(message)
    );
    this._vsCodeApi.postMessage({
      type: 'groups',
      groupList: this.getGroupNames(),
      objectList: this.getObjectNames(),
    });
  }

  saveGroups(groups: Record<string, Group>, groupHierarchy: Record<string, any>): void {
    this._groups = groups;

    const naturalSort = (a: string, b: string) =>
      a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });

    const sortedHierarchy: Record<string, any> = {};
    for (const key of Object.keys(groupHierarchy).sort(naturalSort)) {
      sortedHierarchy[key] = {
        ...groupHierarchy[key],
        faces: [...groupHierarchy[key].faces].sort(naturalSort),
        nodes: [...groupHierarchy[key].nodes].sort(naturalSort),
        volumes: [...(groupHierarchy[key].volumes ?? [])].sort(naturalSort),
        edges: [...(groupHierarchy[key].edges ?? [])].sort(naturalSort),
      };
    }

    this._groupHierarchy = sortedHierarchy;
    groupHierarchyStore.set(sortedHierarchy);

    this.initManagers();

    this._vsCodeApi.postMessage({
      type: 'debugPanel',
      text: 'Actors and hierarchy saved',
    });
  }

  private initManagers(): void {
    if (!this._groups || !this._groupHierarchy) return;
    VisibilityManager.Instance.init(this._groups, this._groupHierarchy);
    CameraManager.Instance.init(this._groups);
  }

  refreshThemeColors(): void {
    if (!this._groups) return;
    for (const group of Object.values(this._groups)) {
      group.applyThemeColor();
    }
    CameraManager.Instance.refreshBoundingBoxTheme();
  }

  getGroupNames(): string[] {
    if (!this._groups) {
      return [];
    }
    return Object.keys(this._groups).filter((key) => key.includes('::'));
  }

  getObjectNames(): string[] {
    if (!this._groupHierarchy) {
      return [];
    }
    return Object.keys(this._groupHierarchy);
  }
}
