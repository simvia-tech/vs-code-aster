import { describe, it, expect } from 'vitest';
import { parseMeshGroupsStdout, allGroupNames } from '../../src/MeshGroups';

const PAYLOAD =
  '{"version":1,"meshName":"cube","meshDimension":3,"groups":{"volumes":["SOLID"],"surfaces":["TOP","BOTTOM"],"edges":[],"nodes":["SUPPORT"]}}';

describe('parseMeshGroupsStdout', () => {
  it('parses a clean single-line JSON payload', () => {
    const r = parseMeshGroupsStdout(PAYLOAD + '\n');
    expect(r?.meshDimension).toBe(3);
    expect(r?.groups.volumes).toEqual(['SOLID']);
  });

  it('ignores leading noise lines injected onto stdout', () => {
    const r = parseMeshGroupsStdout(`Ctrl click to launch VS Code Native REPL\n${PAYLOAD}\n`);
    expect(r?.meshName).toBe('cube');
  });

  it('returns null when no JSON payload is present', () => {
    expect(parseMeshGroupsStdout('some error text\n')).toBeNull();
    expect(parseMeshGroupsStdout('')).toBeNull();
  });
});

describe('allGroupNames', () => {
  it('flattens, dedupes and sorts all group kinds', () => {
    const names = allGroupNames({
      volumes: ['SOLID'],
      surfaces: ['TOP', 'BOTTOM'],
      edges: [],
      nodes: ['SOLID'], // duplicate across kinds
    });
    expect(names).toEqual(['BOTTOM', 'SOLID', 'TOP']);
  });
});
