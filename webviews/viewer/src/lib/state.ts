import { writable } from 'svelte/store';

export type GroupHierarchy = Record<string, { faces: string[]; nodes: string[]; color?: number[] }>;
export type HighlightedGroups = Map<string, number[]>;
export type HiddenObjects = Set<string>;

export type EdgeMode = 'gradual' | 'threshold' | 'show' | 'hide';

export interface Settings {
  hiddenObjectOpacity: number;
  edgeMode: EdgeMode;
  edgeThresholdMultiplier: number;
  groupTransparency: number;
  showOrientationWidget: boolean;
}

export const groupHierarchy = writable<GroupHierarchy>({});
export const highlightedGroups = writable<HighlightedGroups>(new Map());
export const hiddenObjects = writable<HiddenObjects>(new Set());
export const zoomRatio = writable<number>(1);
export const isAtDefaultZoom = writable<boolean>(true);
export const settings = writable<Settings>({
  hiddenObjectOpacity: 0,
  edgeMode: 'threshold',
  edgeThresholdMultiplier: 1,
  groupTransparency: 0.2,
  showOrientationWidget: true,
});

// Map<objectKey, Set<groupName>> — groups NOT shown in sidebar (hidden)
export const sidebarHiddenGroups = writable<Map<string, Set<string>>>(new Map());
