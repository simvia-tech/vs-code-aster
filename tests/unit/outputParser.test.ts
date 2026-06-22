import { describe, it, expect } from 'vitest';
import * as vscode from 'vscode';
import { parseRunOutput } from '../../src/OutputParser';

const exportUri = vscode.Uri.file('/work/case.export');
const commUri = vscode.Uri.file('/work/case.comm');

function commFiles(): Map<string, vscode.Uri> {
  return new Map([['case.comm', commUri]]);
}

function flatten(map: Map<string, vscode.Diagnostic[]>): vscode.Diagnostic[] {
  return [...map.values()].flat();
}

describe('parseRunOutput', () => {
  it('maps a code_aster <E> box message to the CMDTAG line of the active comm file', () => {
    const log = [
      '__file__ = r"/work/case.comm"',
      '.. _run0_cmd5',
      '<E> the operator failed',
      '   more detail',
    ].join('\n');
    const diags = parseRunOutput(log, exportUri, commFiles());
    const onComm = diags.get(commUri.toString());
    expect(onComm).toBeDefined();
    expect(onComm).toHaveLength(1);
    expect(onComm![0].severity).toBe(vscode.DiagnosticSeverity.Error);
    expect(onComm![0].range.start.line).toBe(4); // cmd5 -> 0-based 4
    expect(onComm![0].message).toContain('the operator failed');
    expect(onComm![0].source).toBe('code-aster');
  });

  it('treats <A> as a Warning', () => {
    const log = ['__file__ = r"/work/case.comm"', '.. _run0_cmd2', '<A> minor alarm'].join('\n');
    const diags = parseRunOutput(log, exportUri, commFiles());
    const d = flatten(diags);
    expect(d).toHaveLength(1);
    expect(d[0].severity).toBe(vscode.DiagnosticSeverity.Warning);
    expect(d[0].range.start.line).toBe(1);
  });

  it('does not treat cave status flags like <F>_ABNORMAL_ABORT as a box message', () => {
    const diags = parseRunOutput('<F>_ABNORMAL_ABORT', exportUri, commFiles());
    expect(flatten(diags)).toHaveLength(0);
  });

  it('falls back to the export file when no CMDTAG/comm context precedes the message', () => {
    const diags = parseRunOutput('<E> early failure', exportUri, commFiles());
    const onExport = diags.get(exportUri.toString());
    expect(onExport).toHaveLength(1);
    expect(onExport![0].range.start.line).toBe(0);
  });

  it('maps a Python traceback to the deepest user comm file + line', () => {
    const log = [
      'Traceback (most recent call last):',
      '  File "/work/case.comm", line 12, in <module>',
      '    foo()',
      "NameError: name 'foo' is not defined",
    ].join('\n');
    const diags = parseRunOutput(log, exportUri, commFiles());
    const onComm = diags.get(commUri.toString());
    expect(onComm).toHaveLength(1);
    expect(onComm![0].range.start.line).toBe(11);
    expect(onComm![0].message).toContain('NameError');
  });

  it('parses a SyntaxError block (no traceback header)', () => {
    const log = [
      '  File "/work/case.comm", line 3',
      '    x ===',
      '        ^',
      'SyntaxError: invalid syntax',
    ].join('\n');
    const diags = parseRunOutput(log, exportUri, commFiles());
    const onComm = diags.get(commUri.toString());
    expect(onComm).toHaveLength(1);
    expect(onComm![0].range.start.line).toBe(2);
    expect(onComm![0].message).toContain('SyntaxError');
  });

  it('maps a MED/Fortran-layer error to the export file', () => {
    const diags = parseRunOutput('medlecteur.c [123] : Erreur de lecture', exportUri, commFiles());
    const onExport = diags.get(exportUri.toString());
    expect(onExport).toHaveLength(1);
    expect(onExport![0].message).toContain('Erreur de lecture');
  });

  it('deduplicates identical diagnostics printed twice (stderr + fort.6)', () => {
    const block = [
      'Traceback (most recent call last):',
      '  File "/work/case.comm", line 12, in <module>',
      '    foo()',
      "NameError: name 'foo' is not defined",
    ];
    const log = [...block, '', ...block].join('\n');
    const diags = parseRunOutput(log, exportUri, commFiles());
    expect(diags.get(commUri.toString())).toHaveLength(1);
  });
});
