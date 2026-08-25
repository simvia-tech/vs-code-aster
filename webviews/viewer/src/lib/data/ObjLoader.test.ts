import { describe, it, expect } from 'vitest';
import { ObjLoader } from './ObjLoader';

// Two OBJ "file contexts" exercising every entity kind plus the
// `# elements:` / `# nodes:` headers written by med2obj.py. File B's indices
// must be offset by file A's vertex count.
const FILE_A = [
  '# med2obj-version: 3',
  '# elements: 10',
  '# nodes: 4',
  'v 0 0 0',
  'v 1 0 0',
  'v 0 1 0',
  'f 1 2 3',
  'g TOP',
  'f 1 2 3',
  'ng FIX',
  'p 1',
  'p 2',
].join('\n');

const FILE_B = [
  '# elements: 5',
  '# nodes: 3',
  'v 0 0 1',
  'v 1 0 1',
  'l 2 1', // object-level beam (med2obj v4), before any group
  'vg SOLID',
  'f 1 2 3',
  'eg SIDE',
  'l 1 2',
].join('\n');

async function load() {
  return ObjLoader.loadFiles(
    [FILE_A, FILE_B],
    ['a.obj', 'b.obj'],
    () => {},
    () => {}
  );
}

describe('ObjLoader.loadFiles', () => {
  it('accumulates FEA element/node counts from headers across files', async () => {
    const r = await load();
    expect(r.meshStats).toEqual({ elements: 15, nodes: 7 });
  });

  it('parses vertices, faces, edges and nodes with cross-file index offsets', async () => {
    const r = await load();
    expect(r.vertices).toHaveLength(5);
    expect(r.cells).toHaveLength(3);
    expect(r.nodes).toEqual([0, 1]); // file A p-lines, no offset
    expect(r.edges).toEqual([
      [4, 3],
      [3, 4],
    ]); // file B l-lines, offset by A's 3 vertices
  });

  it('attaches object-level edges to their file, grouped edges to their eg group', async () => {
    const r = await load();
    expect(r.edgeIndexToGroup).toEqual([-1, 0]);
    expect(r.edgeFileGroup).toEqual(['all_b.obj', 'all_b.obj']);
  });

  it('registers per-file skin groups and typed group keys', async () => {
    const r = await load();
    expect(r.faceGroups).toContain('all_a.obj');
    expect(r.faceGroups).toContain('all_b.obj');
    expect(r.faceGroups).toContain('all_a.obj::TOP::face');
    expect(r.volumeGroups).toContain('all_b.obj::SOLID::volume');
    expect(r.nodeGroups).toContain('all_a.obj::FIX::node');
    expect(r.edgeGroups).toContain('all_b.obj::SIDE::edge');
  });

  it('builds the per-skin group hierarchy', async () => {
    const r = await load();
    expect(r.groupHierarchy['all_a.obj'].faces).toEqual(['TOP']);
    expect(r.groupHierarchy['all_a.obj'].nodes).toEqual(['FIX']);
    expect(r.groupHierarchy['all_b.obj'].volumes).toEqual(['SOLID']);
    expect(r.groupHierarchy['all_b.obj'].edges).toEqual(['SIDE']);
  });

  it('invokes the onDebug callback with a summary (no VS Code dependency)', async () => {
    const messages: string[] = [];
    await ObjLoader.loadFiles(
      [FILE_A],
      ['a.obj'],
      () => {},
      () => {},
      (t) => messages.push(t)
    );
    expect(messages.some((m) => m.startsWith('TOTAL:'))).toBe(true);
  });
});
