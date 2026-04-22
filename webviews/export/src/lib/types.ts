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
  max_base: string;
  ncpus: string;
  mpi_nbcpu: string;
  mpi_nbnoeud: string;
  testlist: string;
  expected_diag: string;
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
 * `excludeId` skips the file being re-assigned, so re-picking the same
 * type for an existing row is idempotent.
 *
 * Rules:
 * - Fixed-zero types (e.g. `nom`) always return `0`.
 * - If another file of the same type exists, continue that type's own
 *   sequence: `max(usedUnits >= default) + 1`, or the default if none.
 * - Otherwise (type not yet present), return the highest unit across all
 *   files rounded up to the next multiple of 10 (e.g. 30 → 40, 31 → 40).
 *   Falls back to the type's default when no file has a positive unit.
 */
export function getNextAvailableUnit(
  type: string,
  files: FileDescriptor[],
  excludeId?: string
): string {
  if (isFixedZeroType(type)) {
    return '0';
  }
  const defaultUnit = DEFAULT_UNITS[type as AllowedType];
  if (defaultUnit === undefined) {
    return '0';
  }
  const start = Number(defaultUnit);
  const others = files.filter((f) => f.id !== excludeId);

  const sameTypeAtOrAbove: number[] = [];
  let sameTypePresent = false;
  for (const f of others) {
    if (f.type !== type) {
      continue;
    }
    sameTypePresent = true;
    const n = Number(f.unit);
    if (Number.isInteger(n) && Number.isFinite(start) && start > 0 && n >= start) {
      sameTypeAtOrAbove.push(n);
    }
  }

  if (sameTypePresent) {
    if (sameTypeAtOrAbove.length > 0) {
      return String(Math.max(...sameTypeAtOrAbove) + 1);
    }
    if (Number.isFinite(start) && start > 0) {
      return String(start);
    }
  }

  const allPositive = others.map((f) => Number(f.unit)).filter((n) => Number.isInteger(n) && n > 0);
  if (allPositive.length > 0) {
    const max = Math.max(...allPositive);
    return String((Math.floor(max / 10) + 1) * 10);
  }

  if (Number.isFinite(start) && start > 0) {
    return String(start);
  }
  return '0';
}

export function isInteger(value: string): boolean {
  const trimmed = value.trim();
  if (trimmed === '') {
    return false;
  }
  const n = Number(trimmed);
  return Number.isInteger(n);
}
