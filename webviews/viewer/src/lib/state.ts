import { writable } from 'svelte/store';
import { tweened } from 'svelte/motion';
import { cubicOut } from 'svelte/easing';

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
  showBoundingBox: boolean;
  showWireframe: boolean;
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
  showBoundingBox: false,
  showWireframe: false,
});

// Map<objectKey, Set<groupName>> — groups NOT shown in sidebar (hidden)
export const sidebarHiddenGroups = writable<Map<string, Set<string>>>(new Map());

export const loadingProgress = tweened<number>(0, { duration: 300, easing: cubicOut });
export const loadingMessage = writable<string>('');
export const errorMessage = writable<string>('');

export type BoundingBoxDimensions = { x: number; y: number; z: number } | null;
export const boundingBoxDimensions = writable<BoundingBoxDimensions>(null);
