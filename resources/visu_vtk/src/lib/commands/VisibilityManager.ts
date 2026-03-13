import { Controller } from '../Controller';
import { VtkApp } from '../core/VtkApp';
import { GlobalSettings } from '../settings/GlobalSettings';
import { highlightedGroups, hiddenObjects } from '../state';
import type { Group } from '../data/Group';

export class VisibilityManager {
  private static _i: VisibilityManager;
  groups: Record<string, Group> = {};
  private visibleGroupsByObject: Record<string, number> = {};
  hiddenObjects: Record<string, boolean> = {};
  private highlightedGroupsSet: Set<string> = new Set();

  static get Instance(): VisibilityManager {
    if (!this._i) {
      this._i = new VisibilityManager();
    }
    return this._i;
  }

  init(groups: Record<string, Group>, objects: Record<string, any>): void {
    this.groups = groups;
    this.visibleGroupsByObject = {};
    this.hiddenObjects = {};
    this.highlightedGroupsSet = new Set();

    for (const object in objects) {
      this.visibleGroupsByObject[object] = 0;
      this.hiddenObjects[object] = false;
    }

    hiddenObjects.set(new Set());
    highlightedGroups.set(new Map());
  }

  setVisibility(groupName: string, visible?: boolean): { visible: boolean; color: number[]; isFaceGroup: boolean } | undefined {
    const post = (text: string) => {
      Controller.Instance.getVSCodeAPI().postMessage({ type: 'debugPanel', text });
    };

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

    const color = group.getColor();
    const isFaceGroup = group.isFaceGroup;

    const wasHighlighted = this.highlightedGroupsSet.has(groupName);
    const isHighlighted = typeof visible === 'boolean' ? visible : !wasHighlighted;

    if (isHighlighted) {
      this.highlightedGroupsSet.add(groupName);
      highlightedGroups.update((map) => { map.set(groupName, color); return map; });
    } else {
      this.highlightedGroupsSet.delete(groupName);
      highlightedGroups.update((map) => { map.delete(groupName); return map; });
    }

    if (!this.hiddenObjects[object]) {
      group.setVisibility(isHighlighted);
    }

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

    VtkApp.Instance.getRenderWindow().render();

    return { visible: isHighlighted, color, isFaceGroup };
  }

  toggleObjectVisibility(object: string): boolean {
    const nowVisible = this.hiddenObjects[object];
    this.hiddenObjects[object] = !nowVisible;

    hiddenObjects.update((s) => {
      if (nowVisible) s.delete(object);
      else s.add(object);
      return s;
    });

    const fileGroup = this.groups[object];
    if (fileGroup) {
      if (nowVisible) {
        fileGroup.actor.setVisibility(true);
        const opacity = this.visibleGroupsByObject[object] > 0 ? GlobalSettings.Instance.groupTransparency : 1.0;
        fileGroup.setOpacity(opacity);
      } else {
        const hiddenOpacity = GlobalSettings.Instance.hiddenObjectOpacity;
        if (hiddenOpacity === 0) {
          fileGroup.actor.setVisibility(false);
        } else {
          fileGroup.actor.setVisibility(true);
          fileGroup.setOpacity(hiddenOpacity);
        }
      }
    }

    for (const [groupName, group] of Object.entries(this.groups)) {
      if (group.fileGroup === object) {
        group.actor.setVisibility(nowVisible && this.highlightedGroupsSet.has(groupName));
      }
    }

    VtkApp.Instance.getRenderWindow().render();
    return nowVisible;
  }

  setTransparence(transparent: boolean, object: string): void {
    if (!this.groups || this.hiddenObjects[object]) { return; }
    const meshOpacity = transparent ? GlobalSettings.Instance.groupTransparency : 1;
    const group = this.groups[object];
    group.setOpacity(meshOpacity);
  }

  applyGroupTransparency(): void {
    for (const object in this.visibleGroupsByObject) {
      if (this.hiddenObjects[object]) continue;
      if (this.visibleGroupsByObject[object] > 0) {
        this.groups[object]?.setOpacity(GlobalSettings.Instance.groupTransparency);
      }
    }
    VtkApp.Instance.getRenderWindow().render();
  }

  hideAllOthers(object: string): void {
    for (const key in this.hiddenObjects) {
      if (key === object) continue;
      const isAlreadyHidden = this.hiddenObjects[key];
      if (!isAlreadyHidden) {
        this.toggleObjectVisibility(key);
      }
    }
    if (this.hiddenObjects[object]) {
      this.toggleObjectVisibility(object);
    }
  }

  applyHiddenObjectOpacity(): void {
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

  clear(): void {
    for (const [groupName, group] of Object.entries(this.groups)) {
      if (!group.actor) { continue; }
      if (group.fileGroup === null) { continue; }
      group.setVisibility(false);
    }

    this.highlightedGroupsSet.clear();
    highlightedGroups.set(new Map());

    for (const object in this.visibleGroupsByObject) {
      this.setTransparence(false, object);
      this.visibleGroupsByObject[object] = 0;
    }

    VtkApp.Instance.getRenderWindow().render();
  }
}
