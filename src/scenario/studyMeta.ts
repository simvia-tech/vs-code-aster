// vscode-free FEA metadata + defaults shared by the study webview (imported
// into its Vite bundle) and the extension host. Single source of truth for the
// option lists, topology mapping, and seed values the UI presents.

import { Scenario, Modelization, LoadType } from './spec';

export type GroupKindTag = 'volume' | 'surface' | 'edge' | 'node';

export interface Choice<T> {
  value: T;
  label: string;
  detail: string;
}

export const SCENARIOS: Choice<Scenario>[] = [
  {
    value: 'linear-static',
    label: 'Linear elastic static analysis',
    detail: 'MECA_STATIQUE — elastic material, one BC, one load',
  },
  {
    value: 'nonlinear-static',
    label: 'Nonlinear static analysis',
    detail: 'STAT_NON_LINE — load ramp, time increments, convergence',
  },
  {
    value: 'modal',
    label: 'Modal analysis',
    detail: 'CALC_MODES — stiffness/mass matrices (requires density)',
  },
];

export const MODELIZATIONS: Choice<Modelization>[] = [
  { value: '3D', label: '3D', detail: 'Solid continuum' },
  { value: 'D_PLAN', label: 'D_PLAN', detail: 'Plane strain' },
  { value: 'C_PLAN', label: 'C_PLAN', detail: 'Plane stress' },
  { value: 'AXIS', label: 'AXIS', detail: 'Axisymmetric' },
  { value: 'DKT', label: 'DKT', detail: 'Shell / plate (structural)' },
  { value: 'POU_D_T', label: 'POU_D_T', detail: 'Beam (structural)' },
];

export const LOAD_TYPES: Choice<LoadType>[] = [
  { value: 'PRES_REP', label: 'PRES_REP', detail: 'Pressure on faces/shells' },
  { value: 'FORCE_NODALE', label: 'FORCE_NODALE', detail: 'Nodal force' },
  { value: 'FORCE_FACE', label: 'FORCE_FACE', detail: 'Surface force' },
  { value: 'FORCE_ARETE', label: 'FORCE_ARETE', detail: 'Edge force' },
  { value: 'PESANTEUR', label: 'PESANTEUR', detail: 'Gravity' },
];

/** DOFs that can be imposed for a given modelization. */
export function availableDofs(m: Modelization): string[] {
  switch (m) {
    case '3D':
      return ['DX', 'DY', 'DZ'];
    case 'D_PLAN':
    case 'C_PLAN':
    case 'AXIS':
      return ['DX', 'DY'];
    case 'DKT':
    case 'POU_D_T':
      return ['DX', 'DY', 'DZ', 'DRX', 'DRY', 'DRZ'];
  }
}

/** Element-group kinds usable for material assignment, per modelization. */
export function materialKinds(m: Modelization): GroupKindTag[] {
  switch (m) {
    case '3D':
      return ['volume'];
    case 'POU_D_T':
      return ['edge'];
    default:
      return ['surface'];
  }
}

/** Group kinds a given load type applies to ([] = no group, e.g. gravity). */
export function loadGroupKinds(type: LoadType): GroupKindTag[] {
  switch (type) {
    case 'PRES_REP':
    case 'FORCE_FACE':
      return ['surface'];
    case 'FORCE_ARETE':
      return ['edge'];
    case 'FORCE_NODALE':
      return ['node'];
    case 'PESANTEUR':
      return [];
  }
}

export interface MaterialPreset {
  label: string;
  young: number;
  poisson: number;
  rho: number;
}

export const MATERIAL_PRESETS: MaterialPreset[] = [
  { label: 'Steel', young: 210000, poisson: 0.3, rho: 7800 },
  { label: 'Aluminum', young: 70000, poisson: 0.33, rho: 2700 },
  { label: 'Concrete', young: 30000, poisson: 0.2, rho: 2400 },
];

/** Seed values the wizard/form starts from. */
export const STUDY_DEFAULTS = {
  young: 210000,
  poisson: 0.3,
  rho: 7800,
  yieldStress: 250,
  hardening: 2000,
  thickness: 0.01,
  beamHy: 0.1,
  beamHz: 0.05,
  pressure: 1000,
  forceFz: -1000,
  gravity: 9.81,
  nmodes: 10,
  baseName: 'case',
} as const;

export type StudyDefaults = typeof STUDY_DEFAULTS;

/** Normalize a user-entered study name to a safe folder/concept base name. */
export function sanitizeBaseName(raw: string): string {
  const cleaned = raw
    .trim()
    .replace(/\.(comm|export|med|mmed|rmed)$/i, '')
    .replace(/[^A-Za-z0-9_]/g, '_')
    .replace(/^_+|_+$/g, '');
  return cleaned || 'study';
}
