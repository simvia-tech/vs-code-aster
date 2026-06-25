import { describe, it, expect } from 'vitest';
import {
  checkGlyph,
  ioGlyph,
  severityGlyph,
  countDiagnostics,
  GLYPH_LEGEND,
  CHECK_DOCS,
  ValidationReport,
} from '../../src/validationReport';

describe('checkGlyph', () => {
  it('maps pass / structural-fail / advisory-fail / N-A', () => {
    expect(checkGlyph(true)).toBe('✅');
    expect(checkGlyph(false)).toBe('❌');
    expect(checkGlyph(false, true)).toBe('⚠️');
    expect(checkGlyph(null)).toBe('—');
  });
});

describe('ioGlyph', () => {
  it('maps status to a glyph', () => {
    expect(ioGlyph('ok')).toBe('✅');
    expect(ioGlyph('warning')).toBe('⚠️');
    expect(ioGlyph('error')).toBe('❌');
  });
});

describe('severityGlyph', () => {
  it('maps severity to a glyph', () => {
    expect(severityGlyph('error')).toBe('❌');
    expect(severityGlyph('warning')).toBe('⚠️');
    expect(severityGlyph('information')).toBe('ℹ️');
  });
});

describe('countDiagnostics', () => {
  it('counts by severity', () => {
    const report = {
      commands: [],
      io: [],
      hasExport: true,
      diagnostics: [
        { file: 'comm', line: 0, colStart: 0, colEnd: 1, severity: 'error', code: 'x', message: '' },
        { file: 'comm', line: 0, colStart: 0, colEnd: 1, severity: 'warning', code: 'y', message: '' },
        { file: 'export', line: 0, colStart: 0, colEnd: 1, severity: 'warning', code: 'z', message: '' },
        { file: 'comm', line: 0, colStart: 0, colEnd: 1, severity: 'information', code: 'w', message: '' },
      ],
    } as ValidationReport;
    expect(countDiagnostics(report)).toEqual({ errors: 1, warnings: 2 });
  });
});

describe('legend and column docs', () => {
  it('covers all four glyphs in the legend', () => {
    const text = GLYPH_LEGEND.map((l) => l.text).join(' ');
    expect(text).toContain('passed');
    expect(text).toContain('warning');
    expect(text).toContain('not applicable');
    expect(GLYPH_LEGEND).toHaveLength(4);
  });

  it('documents every command-table check', () => {
    expect(CHECK_DOCS.syntactic).toMatch(/recognised/i);
    expect(CHECK_DOCS.dependency).toMatch(/defined earlier/i);
    expect(CHECK_DOCS.naming).toMatch(/name/i);
    expect(CHECK_DOCS.used).toMatch(/referenced later/i);
  });
});
