export const ALLOWED_TYPES = [
  'nom',
  'comm',
  'med',
  'msh',
  'datg',
  'dat',
  'rmed',
  'mmed',
  'base',
  'mess',
  'libr',
] as const;

export type AllowedType = (typeof ALLOWED_TYPES)[number];

export const DEFAULT_UNITS: Record<AllowedType, string> = {
  nom: '0',
  comm: '1',
  med: '20',
  msh: '19',
  datg: '16',
  dat: '29',
  rmed: '80',
  base: '0',
  mess: '6',
  mmed: '20',
  libr: '16',
};

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

export function getNextAvailableUnit(
  defaultUnit: string,
  inputs: FileDescriptor[],
  outputs: FileDescriptor[]
): string {
  const start = Number(defaultUnit);
  if (!Number.isFinite(start) || start === 0) {
    return '0';
  }
  const used = new Set<string>();
  for (const f of inputs) {
    used.add(String(f.unit));
  }
  for (const f of outputs) {
    used.add(String(f.unit));
  }
  let unit = start;
  while (used.has(String(unit))) {
    unit += 1;
  }
  return String(unit);
}

export function isInteger(value: string): boolean {
  const trimmed = value.trim();
  if (trimmed === '') {
    return false;
  }
  const n = Number(trimmed);
  return Number.isInteger(n);
}
