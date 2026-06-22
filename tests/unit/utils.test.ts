import { describe, it, expect } from 'vitest';
import { getTimezoneOffsetString, getPackageVersion } from '../../src/utils';

describe('getTimezoneOffsetString', () => {
  it('formats as ±HH:MM', () => {
    expect(getTimezoneOffsetString()).toMatch(/^[+-]\d{2}:\d{2}$/);
  });
});

describe('getPackageVersion', () => {
  it('returns a semver-shaped string (or the safe fallback)', () => {
    const v = getPackageVersion();
    expect(typeof v).toBe('string');
    expect(v).toMatch(/^\d+\.\d+\.\d+/);
  });
});
