export const ALLOWED_TYPES = [
  'comm',
  'mmed',
  'rmed',
  'mess',
  'nom',
  'base',
  'mail',
  'libr',
  'tab',
  'msh',
  'dat',
] as const;

export type AllowedType = (typeof ALLOWED_TYPES)[number];

// Types that can appear as inputs (code_aster reads them).
export const INPUT_TYPES: readonly AllowedType[] = [
  'comm',
  'mmed',
  'nom',
  'base',
  'mail',
  'libr',
  'msh',
  'dat',
];

// Types that can appear as outputs (code_aster writes them).
export const OUTPUT_TYPES: readonly AllowedType[] = [
  'mmed',
  'rmed',
  'mess',
  'base',
  'mail',
  'tab',
  'msh',
  'dat',
];

export const DEFAULT_UNITS: Record<AllowedType, string> = {
  nom: '0',
  comm: '1',
  mail: '19',
  mmed: '20',
  rmed: '80',
  mess: '6',
  base: '0',
  libr: '16',
  msh: '19',
  dat: '29',
  tab: '30',
};

// Types whose unit is always 0 (the file is selected by name, not I/O unit).
// Multiple files of these types can legitimately share unit 0.
export const FIXED_ZERO_TYPES: readonly AllowedType[] = ['nom'];

export function isFixedZeroType(type: string): boolean {
  return (FIXED_ZERO_TYPES as readonly string[]).includes(type);
}

export interface FileDescriptor {
  id: string;
  type: string;
  name: string;
  unit: string;
}

export interface Parameters {
  time_limit: string;
  memory_limit: string;
  ncpus: string;
  mpi_nbcpu: string;
  mpi_nbnoeud: string;
}

export interface FormData {
  name: string;
  parameters: Parameters;
  inputFiles: FileDescriptor[];
  outputFiles: FileDescriptor[];
}

let rowCounter = 0;
export function newRowId(prefix = 'row'): string {
  rowCounter += 1;
  return `${prefix}-${rowCounter}`;
}

/**
 * Returns the next integer unit for a file of the given `type`.
 * Scoped to same-type rows only (so `comm` numbering does not jump over
 * unrelated `med` units). `excludeId` skips the file being re-assigned,
 * so re-picking the same type for an existing row is idempotent.
 *
 * Rule: start at the type's default. If any same-type unit is >= default,
 * return `max(usedUnits >= default) + 1`; otherwise return the default.
 */
export function getNextAvailableUnit(
  type: string,
  files: FileDescriptor[],
  excludeId?: string
): string {
  const defaultUnit = DEFAULT_UNITS[type as AllowedType];
  if (defaultUnit === undefined) {
    return '0';
  }
  const start = Number(defaultUnit);
  if (!Number.isFinite(start) || start === 0) {
    return '0';
  }
  const usedAtOrAbove: number[] = [];
  for (const f of files) {
    if (f.id === excludeId) {
      continue;
    }
    if (f.type !== type) {
      continue;
    }
    const n = Number(f.unit);
    if (Number.isInteger(n) && n >= start) {
      usedAtOrAbove.push(n);
    }
  }
  if (usedAtOrAbove.length === 0) {
    return String(start);
  }
  return String(Math.max(...usedAtOrAbove) + 1);
}

export function isInteger(value: string): boolean {
  const trimmed = value.trim();
  if (trimmed === '') {
    return false;
  }
  const n = Number(trimmed);
  return Number.isInteger(n);
}
