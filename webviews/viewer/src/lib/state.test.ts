import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { groupNameMatches, settings } from './state';

describe('groupNameMatches', () => {
  it('matches case-insensitively as a substring', () => {
    expect(groupNameMatches('CLAMPED_EDGE', 'clamp')).toBe(true);
    expect(groupNameMatches('clamped_edge', 'EDGE')).toBe(true);
    expect(groupNameMatches('LOAD_FACE', 'face')).toBe(true);
  });

  it('ignores surrounding whitespace in the term', () => {
    expect(groupNameMatches('SUPPORT', '  support ')).toBe(true);
  });

  it('returns false for an empty term and for non-matches', () => {
    expect(groupNameMatches('ANY', '')).toBe(false);
    expect(groupNameMatches('ANY', '   ')).toBe(false);
    expect(groupNameMatches('SOLID', 'shell')).toBe(false);
  });
});

describe('settings store defaults', () => {
  it('exposes the expected default snapshot', () => {
    const s = get(settings);
    expect(s.edgeMode).toBe('threshold');
    expect(s.sidebarSort).toBe('natural');
    expect(s.groupByKind).toBe(true);
    expect(s.showBoundingBox).toBe(false);
    expect(s.autoRotateSpeed).toBe(15);
  });
});
