/**
 * Data model for the "Generate study from scenario" feature. `StudySpec` is the
 * single value collected by the wizard and consumed by the pure generators
 * (`generateComm`, `generateExport`). It carries no VS Code / filesystem state,
 * so the generators are trivially unit-testable.
 */

export type Scenario = 'linear-static' | 'nonlinear-static' | 'modal';

/** AFFE_MODELE MODELISATION values supported by the first version. */
export type Modelization = '3D' | 'D_PLAN' | 'C_PLAN' | 'AXIS' | 'DKT' | 'POU_D_T';

/** Modelizations that require AFFE_CARA_ELEM (structural elements). */
export const STRUCTURAL_MODELIZATIONS: readonly Modelization[] = ['DKT', 'POU_D_T'];

export function isStructuralModelization(m: Modelization): boolean {
  return STRUCTURAL_MODELIZATIONS.includes(m);
}

export interface MaterialSpec {
  /** Young's modulus E. */
  young: number;
  /** Poisson's ratio NU. */
  poisson: number;
  /** Density RHO — required for modal analysis (mass matrix). */
  rho?: number;
  /** Yield stress SY — enables an elastoplastic (VMIS_ISOT_LINE) nonlinear law. */
  yieldStress?: number;
  /** Linear hardening slope D_SIGM_EPSI for ECRO_LINE. */
  hardening?: number;
}

export type GroupKind = 'GROUP_MA' | 'GROUP_NO';

/** Shell element properties (COQUE) for DKT and similar. */
export interface ShellProps {
  kind: 'shell';
  groups: string[];
  /** Shell thickness EPAIS. */
  thickness: number;
}

/** Beam section (POUTRE) for POU_D_T and similar. */
export interface BeamProps {
  kind: 'beam';
  groups: string[];
  section: { type: 'CERCLE'; R: number } | { type: 'RECTANGLE'; HY: number; HZ: number };
}

export type StructuralProps = ShellProps | BeamProps;

export interface BoundaryCondition {
  groups: string[];
  groupKind: GroupKind;
  /** Imposed DOFs, e.g. { DX: 0, DY: 0, DZ: 0 }. Emitted in canonical order. */
  dofs: Record<string, number>;
}

export type LoadType = 'PRES_REP' | 'FORCE_FACE' | 'FORCE_ARETE' | 'FORCE_NODALE' | 'PESANTEUR';

export interface LoadSpec {
  type: LoadType;
  groups: string[];
  groupKind: GroupKind;
  /** Scalar value: pressure for PRES_REP, gravity for PESANTEUR. */
  value?: number;
  /** Force components / gravity direction. */
  components?: { FX?: number; FY?: number; FZ?: number };
}

export interface ModalParams {
  /** Number of modes to extract (CALC_FREQ NMAX_FREQ). */
  nmodes: number;
}

export interface StudySpec {
  scenario: Scenario;
  modelization: Modelization;
  /** True when the modelization needs AFFE_CARA_ELEM (derived; stored for clarity). */
  isStructural: boolean;
  /** Mesh file name as referenced by the .export `F mmed` line, e.g. "mesh.med". */
  meshFileName: string;
  /** Study base name driving <baseName>.comm / .export / .mess / .rmed. */
  baseName: string;
  material: MaterialSpec;
  /** Material assignment groups; empty => TOUT='OUI'. */
  materialGroups: string[];
  structuralProps?: StructuralProps;
  boundaryConditions: BoundaryCondition[];
  /** Mechanical load; omitted for modal analysis. */
  load?: LoadSpec;
  /** Modal extraction parameters; only for the modal scenario. */
  modal?: ModalParams;
  /** Emit a header comment block (default true). */
  comments?: boolean;
}
