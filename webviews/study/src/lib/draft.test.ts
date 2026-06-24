import { describe, it, expect } from 'vitest';
import { defaultDraft, draftToSpec, validateDraft, taggedGroups, type Draft } from './draft';
import { generateComm } from '@scenario/generateComm';
import { generateExport } from '@scenario/generateExport';

function base(): Draft {
  const d = defaultDraft('mesh.med');
  d.materialGroups = [{ name: 'SOLID', kind: 'volume' }];
  d.bcGroups = [{ name: 'CLAMP', kind: 'surface' }];
  d.loadGroups = [{ name: 'LOAD_FACE', kind: 'surface' }];
  d.loadValue = '100000';
  return d;
}

describe('draftToSpec', () => {
  it('linear-static 3D default → MECA_STATIQUE, no CARA_ELEM', () => {
    const spec = draftToSpec(base());
    expect(spec.scenario).toBe('linear-static');
    expect(spec.isStructural).toBe(false);
    const comm = generateComm(spec);
    expect(comm).toContain('MECA_STATIQUE');
    expect(comm).not.toContain('AFFE_CARA_ELEM');
  });

  it('shell DKT → shell props + CARA_ELEM wiring', () => {
    const d = base();
    d.modelization = 'DKT';
    d.structuralGroups = [{ name: 'PANEL', kind: 'surface' }];
    d.shellThickness = '0.01';
    const spec = draftToSpec(d);
    expect(spec.isStructural).toBe(true);
    expect(spec.structuralProps).toEqual({ kind: 'shell', groups: ['PANEL'], thickness: 0.01 });
    const comm = generateComm(spec);
    expect(comm).toContain('AFFE_CARA_ELEM');
    expect(comm).toContain('CARA_ELEM=element_properties');
  });

  it('beam POU_D_T → beam section', () => {
    const d = base();
    d.modelization = 'POU_D_T';
    d.structuralGroups = [{ name: 'BEAM', kind: 'edge' }];
    const spec = draftToSpec(d);
    expect(spec.structuralProps).toEqual({
      kind: 'beam',
      groups: ['BEAM'],
      section: { type: 'RECTANGLE', HY: 0.1, HZ: 0.05 },
    });
  });

  it('modal → modal params + density, no load', () => {
    const d = base();
    d.scenario = 'modal';
    const spec = draftToSpec(d);
    expect(spec.modal).toEqual({ nmodes: 10 });
    expect(spec.load).toBeUndefined();
    expect(spec.material.rho).toBe(7800);
    const comm = generateComm(spec);
    expect(comm).toContain('CALC_MODES');
    expect(comm).toContain('RHO=7800.0');
  });

  it('nonlinear → STAT_NON_LINE with yield stress', () => {
    const d = base();
    d.scenario = 'nonlinear-static';
    const spec = draftToSpec(d);
    expect(spec.material.yieldStress).toBe(250);
    expect(generateComm(spec)).toContain('STAT_NON_LINE');
  });

  it('splits BC groups into GROUP_MA (element) and GROUP_NO (node)', () => {
    const d = base();
    d.bcGroups = [
      { name: 'CLAMP', kind: 'surface' },
      { name: 'PINS', kind: 'node' },
    ];
    const spec = draftToSpec(d);
    expect(spec.boundaryConditions.map((b) => b.groupKind).sort()).toEqual([
      'GROUP_MA',
      'GROUP_NO',
    ]);
  });

  it('keeps logical units consistent between .comm and .export', () => {
    const spec = draftToSpec(base());
    expect(generateComm(spec)).toContain('UNITE=20');
    expect(generateExport(spec)).toMatch(/mmed mesh\.med D 20/);
  });
});

describe('validateDraft', () => {
  it('passes for a complete linear-static draft', () => {
    expect(validateDraft(base())).toEqual([]);
  });
  it('flags a non-numeric Young modulus', () => {
    const d = base();
    d.young = 'abc';
    expect(validateDraft(d).some((e) => /Young/.test(e.message))).toBe(true);
  });
  it('requires a loaded group for non-gravity loads', () => {
    const d = base();
    d.loadGroups = [];
    expect(validateDraft(d).some((e) => /loaded group/.test(e.message))).toBe(true);
  });
  it('requires density for modal', () => {
    const d = base();
    d.scenario = 'modal';
    d.rho = '';
    expect(validateDraft(d).some((e) => /density/.test(e.message))).toBe(true);
  });
  it('requires a boundary-condition group', () => {
    const d = base();
    d.bcGroups = [];
    expect(validateDraft(d).some((e) => /boundary-condition group/.test(e.message))).toBe(true);
  });
  it('requires structural groups for shell/beam modelizations', () => {
    const d = base();
    d.modelization = 'DKT';
    d.structuralGroups = [];
    expect(validateDraft(d).some((e) => /shell group/.test(e.message))).toBe(true);
  });
  it('ties each error to a field id', () => {
    const d = base();
    d.young = 'abc';
    const err = validateDraft(d).find((e) => /Young/.test(e.message));
    expect(err?.id).toBe('study-young');
  });
});

describe('taggedGroups', () => {
  it('filters mesh groups by requested kinds', () => {
    const groups = { volumes: ['V'], surfaces: ['S1', 'S2'], edges: ['E'], nodes: ['N'] };
    expect(taggedGroups(groups, ['surface']).map((g) => g.name)).toEqual(['S1', 'S2']);
    expect(taggedGroups(groups, ['volume', 'node']).map((g) => g.kind)).toEqual(['volume', 'node']);
  });
});
