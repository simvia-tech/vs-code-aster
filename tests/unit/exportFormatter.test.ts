import { describe, it, expect } from 'vitest';
import { formatExportContent } from '../../src/ExportFormatter';

const STATIC_HEADER = '# This file was generated using VS Code Aster';

describe('formatExportContent', () => {
  it('emits only the static header for empty input', () => {
    const out = formatExportContent('');
    expect(out).toContain(STATIC_HEADER);
    expect(out).not.toContain('# Input files');
    expect(out).not.toContain('# Output files');
    expect(out.endsWith('\n')).toBe(true);
  });

  it('prepends a filename header when given', () => {
    const out = formatExportContent('F comm case.comm D 1', 'case.export');
    expect(out.split('\n')[0]).toBe('# case.export');
  });

  it('splits inputs (D) and outputs (R) into sections', () => {
    const raw = ['F rmed case.rmed R 80', 'F comm case.comm D 1', 'F mmed mesh.med D 20'].join(
      '\n'
    );
    const out = formatExportContent(raw);
    expect(out).toContain('# Input files');
    expect(out).toContain('# Output files');
    const inputsIdx = out.indexOf('# Input files');
    const outputsIdx = out.indexOf('# Output files');
    expect(inputsIdx).toBeLessThan(outputsIdx);
    // comm input appears before its output section
    expect(out.indexOf('F comm case.comm D 1')).toBeLessThan(outputsIdx);
    expect(out.indexOf('F rmed case.rmed R 80')).toBeGreaterThan(outputsIdx);
  });

  it('orders input F-lines by the canonical type order (comm before mmed)', () => {
    const raw = ['F mmed mesh.med D 20', 'F comm case.comm D 1'].join('\n');
    const out = formatExportContent(raw);
    expect(out.indexOf('F comm case.comm D 1')).toBeLessThan(out.indexOf('F mmed mesh.med D 20'));
  });

  it('groups P parameters under the parameters section', () => {
    const out = formatExportContent('P time_limit 300');
    expect(out).toContain('# Simulation parameters');
    expect(out).toContain('P time_limit 300');
  });

  it('keeps user comments attached to the following entry', () => {
    const raw = ['# my mesh', 'F mmed mesh.med D 20'].join('\n');
    const out = formatExportContent(raw);
    const lines = out.split('\n');
    const meshIdx = lines.indexOf('F mmed mesh.med D 20');
    expect(lines[meshIdx - 1]).toBe('# my mesh');
  });

  it('normalizes CRLF line endings', () => {
    const out = formatExportContent('F comm case.comm D 1\r\nF mmed mesh.med D 20\r\n');
    expect(out).not.toContain('\r');
  });

  it('routes malformed F-lines to the unknown section', () => {
    const out = formatExportContent('F comm case.comm X 1'); // invalid IO flag
    expect(out).toContain('# Unknown lines');
    expect(out).toContain('F comm case.comm X 1');
  });

  it('is idempotent: formatting its own output drops the auto headers and re-emits them once', () => {
    const once = formatExportContent('F comm case.comm D 1\nF mmed mesh.med D 20', 'case.export');
    const twice = formatExportContent(once, 'case.export');
    expect(twice).toBe(once);
  });
});
