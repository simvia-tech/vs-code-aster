import { VtkApp } from './core/VtkApp';
import { CreateGroups } from './data/CreateGroups';
import { VisibilityManager } from './commands/VisibilityManager';
import { CameraManager } from './interaction/CameraManager';
import { GlobalSettings } from './settings/GlobalSettings';
import { groupHierarchy as groupHierarchyStore, loadingProgress, loadingMessage } from './state';
import type { Group, GroupKind } from './data/Group';

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
    this._groupHierarchy = this.buildSortedHierarchy(groupHierarchy);
    groupHierarchyStore.set(this._groupHierarchy);

    this.initManagers();

    this._vsCodeApi.postMessage({
      type: 'debugPanel',
      text: 'Actors and hierarchy saved',
    });
  }

  applySortOrder(): void {
    if (!this._groupHierarchy) return;
    this._groupHierarchy = this.buildSortedHierarchy(this._groupHierarchy);
    groupHierarchyStore.set(this._groupHierarchy);
  }

  private buildSortedHierarchy(hierarchy: Record<string, any>): Record<string, any> {
    const naturalSort = (a: string, b: string) =>
      a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });

    const sortOrder = GlobalSettings.Instance.sidebarSort;
    const groups = this._groups;

    const sortKind = (skinKey: string, kind: GroupKind, names: string[]): string[] => {
      if (sortOrder === 'size' && groups) {
        const sized = names.map((name) => {
          const g = groups[`${skinKey}::${name}::${kind}`];
          return { name, size: g?.cellCount ?? 0 };
        });
        sized.sort((a, b) => b.size - a.size || naturalSort(a.name, b.name));
        return sized.map((s) => s.name);
      }
      return [...names].sort(naturalSort);
    };

    const buildMixed = (
      skinKey: string,
      volumes: string[],
      faces: string[],
      edges: string[],
      nodes: string[]
    ): { name: string; kind: GroupKind }[] => {
      const all: { name: string; kind: GroupKind; size: number }[] = [
        ...volumes.map((name) => ({ name, kind: 'volume' as GroupKind, size: 0 })),
        ...faces.map((name) => ({ name, kind: 'face' as GroupKind, size: 0 })),
        ...edges.map((name) => ({ name, kind: 'edge' as GroupKind, size: 0 })),
        ...nodes.map((name) => ({ name, kind: 'node' as GroupKind, size: 0 })),
      ];
      if (sortOrder === 'size' && groups) {
        for (const item of all) {
          item.size = groups[`${skinKey}::${item.name}::${item.kind}`]?.cellCount ?? 0;
        }
        all.sort((a, b) => b.size - a.size || naturalSort(a.name, b.name));
      } else {
        all.sort((a, b) => naturalSort(a.name, b.name));
      }
      return all.map(({ name, kind }) => ({ name, kind }));
    };

    const sorted: Record<string, any> = {};
    for (const key of Object.keys(hierarchy).sort(naturalSort)) {
      const data = hierarchy[key];
      const volumes = sortKind(key, 'volume', data.volumes ?? []);
      const faces = sortKind(key, 'face', data.faces ?? []);
      const edges = sortKind(key, 'edge', data.edges ?? []);
      const nodes = sortKind(key, 'node', data.nodes ?? []);
      sorted[key] = {
        ...data,
        volumes,
        faces,
        edges,
        nodes,
        mixed: buildMixed(key, volumes, faces, edges, nodes),
      };
    }
    return sorted;
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
