import { describe, it, expect, beforeEach } from 'vitest';
import {
  ALLOWED_TYPES,
  INPUT_TYPES,
  OUTPUT_TYPES,
  DEFAULT_UNITS,
  isFixedZeroType,
  isInteger,
  newRowId,
  getNextAvailableUnit,
  type FileDescriptor,
} from './types';

function file(type: string, unit: string, id = newRowId()): FileDescriptor {
  return { id, type, name: `${type}.dat`, unit };
}

describe('type tables', () => {
  it('DEFAULT_UNITS has an entry for every allowed type', () => {
    for (const t of ALLOWED_TYPES) {
      expect(DEFAULT_UNITS[t]).toBeDefined();
    }
  });

  it('input/output type sets only contain allowed types', () => {
    for (const t of [...INPUT_TYPES, ...OUTPUT_TYPES]) {
      expect(ALLOWED_TYPES).toContain(t);
    }
  });

  it('comm is input-only, rmed/mess are output-only', () => {
    expect(INPUT_TYPES).toContain('comm');
    expect(OUTPUT_TYPES).not.toContain('comm');
    expect(OUTPUT_TYPES).toContain('rmed');
    expect(INPUT_TYPES).not.toContain('rmed');
    expect(OUTPUT_TYPES).toContain('mess');
    expect(INPUT_TYPES).not.toContain('mess');
  });
});

describe('isFixedZeroType', () => {
  it('is true only for nom', () => {
    expect(isFixedZeroType('nom')).toBe(true);
    expect(isFixedZeroType('comm')).toBe(false);
    expect(isFixedZeroType('mmed')).toBe(false);
  });
});

describe('isInteger', () => {
  it('accepts integer strings (incl. surrounding whitespace)', () => {
    expect(isInteger('0')).toBe(true);
    expect(isInteger('42')).toBe(true);
    expect(isInteger('  7 ')).toBe(true);
    expect(isInteger('-3')).toBe(true);
  });

  it('rejects empty / non-integer strings', () => {
    expect(isInteger('')).toBe(false);
    expect(isInteger('   ')).toBe(false);
    expect(isInteger('3.5')).toBe(false);
    expect(isInteger('abc')).toBe(false);
  });
});

describe('newRowId', () => {
  it('produces unique, monotonically suffixed ids', () => {
    const a = newRowId();
    const b = newRowId();
    expect(a).not.toBe(b);
    expect(a).toMatch(/^row-\d+$/);
  });

  it('honors a custom prefix', () => {
    expect(newRowId('file')).toMatch(/^file-\d+$/);
  });
});

describe('getNextAvailableUnit', () => {
  let files: FileDescriptor[];
  beforeEach(() => {
    files = [];
  });

  it('returns 0 for fixed-zero types regardless of state', () => {
    expect(getNextAvailableUnit('nom', files)).toBe('0');
    files.push(file('nom', '0'));
    expect(getNextAvailableUnit('nom', files)).toBe('0');
  });

  it('returns the type default when no files exist', () => {
    expect(getNextAvailableUnit('comm', files)).toBe('1');
    expect(getNextAvailableUnit('mmed', files)).toBe('20');
    expect(getNextAvailableUnit('rmed', files)).toBe('80');
  });

  it('continues the same-type sequence (max + 1) when the type is present', () => {
    files = [file('mmed', '20'), file('mmed', '21')];
    expect(getNextAvailableUnit('mmed', files)).toBe('22');
  });

  it('returns the type default when same type present but none at/above default', () => {
    files = [file('mmed', '5')];
    expect(getNextAvailableUnit('mmed', files)).toBe('20');
  });

  it('rounds up to the next decade when introducing a new type alongside others', () => {
    files = [file('mess', '6'), file('rmed', '80')];
    // highest positive unit is 80 -> next decade 90
    expect(getNextAvailableUnit('tab', files)).toBe('90');
  });

  it('rounds 31 up to 40 for a new type', () => {
    files = [file('dat', '31')];
    expect(getNextAvailableUnit('tab', files)).toBe('40');
  });

  it('respects excludeId so re-picking a type for an existing row is idempotent', () => {
    const row = file('mmed', '20', 'row-x');
    files = [row];
    // Excluding the row itself, no mmed remains -> default 20.
    expect(getNextAvailableUnit('mmed', files, 'row-x')).toBe('20');
  });

  it('returns 0 when no positive units exist for an unknown type', () => {
    expect(getNextAvailableUnit('does-not-exist', files)).toBe('0');
  });
});
