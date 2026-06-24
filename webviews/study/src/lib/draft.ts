// Pure draft model + StudySpec assembly for the study webview. No DOM/Svelte
// imports, so it is unit-testable and the single place the form's state becomes
// the StudySpec wire contract.

import type {
  StudySpec,
  Scenario,
  Modelization,
  LoadType,
  BoundaryCondition,
  StructuralProps,
  LoadSpec,
} from '@scenario/spec';
import { isStructuralModelization } from '@scenario/spec';
import {
  GroupKindTag,
  loadGroupKinds,
  availableDofs,
  STUDY_DEFAULTS,
  sanitizeBaseName,
} from '@scenario/studyMeta';

export interface TaggedGroup {
  name: string;
  kind: GroupKindTag;
}

/** Mesh groups by topology, as sent by the host (mirrors src/MeshGroups.ts
 * without importing it — that module pulls in vscode). */
export interface MeshGroups {
  volumes: string[];
  surfaces: string[];
  edges: string[];
  nodes: string[];
}

/** Flatten the mesh groups of the requested kinds into tagged candidates. */
export function taggedGroups(groups: MeshGroups, kinds: GroupKindTag[]): TaggedGroup[] {
  const map: Record<GroupKindTag, string[]> = {
    volume: groups.volumes,
    surface: groups.surfaces,
    edge: groups.edges,
    node: groups.nodes,
  };
  const out: TaggedGroup[] = [];
  for (const kind of kinds) {
    for (const name of map[kind]) {
      out.push({ name, kind });
    }
  }
  return out;
}

/** All form state. Numbers are kept as strings (raw input) until assembly. */
export interface Draft {
  scenario: Scenario;
  modelization: Modelization;
  young: string;
  poisson: string;
  rho: string;
  yieldStress: string;
  hardening: string;
  materialGroups: TaggedGroup[];
  structuralGroups: TaggedGroup[];
  shellThickness: string;
  beamHy: string;
  beamHz: string;
  bcGroups: TaggedGroup[];
  bcDofs: string[];
  loadType: LoadType;
  loadGroups: TaggedGroup[];
  loadValue: string;
  nmodes: string;
  baseName: string;
  meshFileName: string;
}

export function defaultDraft(meshFileName = ''): Draft {
  return {
    scenario: 'linear-static',
    modelization: '3D',
    young: String(STUDY_DEFAULTS.young),
    poisson: String(STUDY_DEFAULTS.poisson),
    rho: String(STUDY_DEFAULTS.rho),
    yieldStress: String(STUDY_DEFAULTS.yieldStress),
    hardening: String(STUDY_DEFAULTS.hardening),
    materialGroups: [],
    structuralGroups: [],
    shellThickness: String(STUDY_DEFAULTS.thickness),
    beamHy: String(STUDY_DEFAULTS.beamHy),
    beamHz: String(STUDY_DEFAULTS.beamHz),
    bcGroups: [],
    bcDofs: availableDofs('3D'),
    loadType: 'PRES_REP',
    loadGroups: [],
    loadValue: String(STUDY_DEFAULTS.pressure),
    nmodes: String(STUDY_DEFAULTS.nmodes),
    baseName: STUDY_DEFAULTS.baseName,
    meshFileName,
  };
}

function names(groups: TaggedGroup[]): string[] {
  return groups.map((g) => g.name);
}

/** Assemble a StudySpec from the draft. Pure; mirrors the old buildSpec. */
export function draftToSpec(draft: Draft): StudySpec {
  const isStructural = isStructuralModelization(draft.modelization);

  const dofs: Record<string, number> = {};
  for (const d of draft.bcDofs) {
    dofs[d] = 0;
  }
  const boundaryConditions: BoundaryCondition[] = [];
  const bcElem = draft.bcGroups.filter((g) => g.kind !== 'node').map((g) => g.name);
  const bcNode = draft.bcGroups.filter((g) => g.kind === 'node').map((g) => g.name);
  if (bcElem.length > 0) {
    boundaryConditions.push({ groups: bcElem, groupKind: 'GROUP_MA', dofs });
  }
  if (bcNode.length > 0) {
    boundaryConditions.push({ groups: bcNode, groupKind: 'GROUP_NO', dofs });
  }

  let structuralProps: StructuralProps | undefined;
  if (isStructural) {
    structuralProps =
      draft.modelization === 'DKT'
        ? {
            kind: 'shell',
            groups: names(draft.structuralGroups),
            thickness: Number(draft.shellThickness),
          }
        : {
            kind: 'beam',
            groups: names(draft.structuralGroups),
            section: { type: 'RECTANGLE', HY: Number(draft.beamHy), HZ: Number(draft.beamHz) },
          };
  }

  let load: LoadSpec | undefined;
  if (draft.scenario !== 'modal') {
    const groupKind = loadGroupKinds(draft.loadType)[0] === 'node' ? 'GROUP_NO' : 'GROUP_MA';
    const value = Number(draft.loadValue);
    if (draft.loadType === 'PRES_REP') {
      load = { type: 'PRES_REP', groups: names(draft.loadGroups), groupKind, value };
    } else if (draft.loadType === 'PESANTEUR') {
      load = { type: 'PESANTEUR', groups: [], groupKind: 'GROUP_MA', value };
    } else {
      load = {
        type: draft.loadType,
        groups: names(draft.loadGroups),
        groupKind,
        components: { FZ: value },
      };
    }
  }

  return {
    scenario: draft.scenario,
    modelization: draft.modelization,
    isStructural,
    meshFileName: draft.meshFileName || 'mesh.med',
    baseName: sanitizeBaseName(draft.baseName),
    material: {
      young: Number(draft.young),
      poisson: Number(draft.poisson),
      rho: draft.scenario === 'modal' ? Number(draft.rho) : undefined,
      yieldStress: draft.scenario === 'nonlinear-static' ? Number(draft.yieldStress) : undefined,
      hardening: draft.scenario === 'nonlinear-static' ? Number(draft.hardening) : undefined,
    },
    materialGroups: names(draft.materialGroups),
    structuralProps,
    boundaryConditions,
    load,
    modal: draft.scenario === 'modal' ? { nmodes: Number(draft.nmodes) } : undefined,
  };
}

const isNum = (s: string) => s.trim() !== '' && Number.isFinite(Number(s));

/** DOM ids of the form fields, so a validation error can scroll/focus its
 * field (used by both the form markup and validateDraft). */
export const FIELD = {
  young: 'study-young',
  poisson: 'study-poisson',
  rho: 'study-rho',
  yield: 'study-yield',
  hardening: 'study-hardening',
  thickness: 'study-thickness',
  beamHy: 'study-beam-hy',
  beamHz: 'study-beam-hz',
  structuralGroups: 'study-structural-groups',
  bcGroups: 'study-bc-groups',
  loadGroups: 'study-load-groups',
  loadValue: 'study-load-value',
  nmodes: 'study-nmodes',
  baseName: 'study-basename',
} as const;

export interface ValidationError {
  /** DOM id of the field to focus when the error is clicked. */
  id: string;
  message: string;
}

/** Returns validation problems, each tied to a field id (empty = valid). */
export function validateDraft(draft: Draft): ValidationError[] {
  const errors: ValidationError[] = [];
  const add = (id: string, message: string) => errors.push({ id, message });

  if (!isNum(draft.young)) {
    add(FIELD.young, 'Young’s modulus must be a number.');
  }
  if (!isNum(draft.poisson)) {
    add(FIELD.poisson, 'Poisson’s ratio must be a number.');
  }
  if (draft.scenario === 'modal' && !isNum(draft.rho)) {
    add(FIELD.rho, 'Modal analysis requires a numeric density (RHO).');
  }
  if (draft.scenario === 'nonlinear-static') {
    if (!isNum(draft.yieldStress)) {
      add(FIELD.yield, 'Yield stress (SY) must be a number.');
    }
    if (!isNum(draft.hardening)) {
      add(FIELD.hardening, 'Hardening (D_SIGM_EPSI) must be a number.');
    }
  }
  if (isStructuralModelization(draft.modelization)) {
    if (draft.structuralGroups.length === 0) {
      add(
        FIELD.structuralGroups,
        draft.modelization === 'DKT'
          ? 'Select at least one shell group.'
          : 'Select at least one beam group.'
      );
    }
    if (draft.modelization === 'DKT' && !isNum(draft.shellThickness)) {
      add(FIELD.thickness, 'Shell thickness must be a number.');
    }
    if (draft.modelization === 'POU_D_T' && !isNum(draft.beamHy)) {
      add(FIELD.beamHy, 'Beam section HY must be a number.');
    }
    if (draft.modelization === 'POU_D_T' && !isNum(draft.beamHz)) {
      add(FIELD.beamHz, 'Beam section HZ must be a number.');
    }
  }
  if (draft.bcGroups.length === 0) {
    add(FIELD.bcGroups, 'Select at least one boundary-condition group.');
  }
  if (
    draft.scenario !== 'modal' &&
    draft.loadType !== 'PESANTEUR' &&
    draft.loadGroups.length === 0
  ) {
    add(FIELD.loadGroups, 'Select at least one loaded group (or use gravity).');
  }
  if (draft.scenario !== 'modal' && !isNum(draft.loadValue)) {
    add(FIELD.loadValue, 'Load magnitude must be a number.');
  }
  if (
    draft.scenario === 'modal' &&
    (!Number.isInteger(Number(draft.nmodes)) || Number(draft.nmodes) <= 0)
  ) {
    add(FIELD.nmodes, 'Number of modes must be a positive integer.');
  }
  if (draft.baseName.trim() === '') {
    add(FIELD.baseName, 'Enter a study name.');
  }
  return errors;
}
