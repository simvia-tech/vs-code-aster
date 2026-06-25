import { describe, it, expect } from 'vitest';
import { render, waitFor } from '@testing-library/svelte';
import App from './App.svelte';
import type { ValidationReport } from '@report';

const REPORT: ValidationReport = {
  hasExport: true,
  commands: [
    {
      concept: 'mesh',
      command: 'LIRE_MAILLAGE',
      line: 1,
      syntactic: true,
      dependency: true,
      naming: true,
      used: true,
    },
    {
      concept: '[noname]',
      command: 'IMPR_RESU',
      line: 8,
      syntactic: true,
      dependency: true,
      naming: true,
      used: null,
    },
  ],
  io: [
    { unit: 20, direction: 'Input', file: 'mesh.med', exportType: 'mmed', usedIn: 'LIRE_MAILLAGE', status: 'ok' },
  ],
  diagnostics: [
    {
      file: 'comm',
      line: 4,
      colStart: 0,
      colEnd: 5,
      severity: 'warning',
      code: 'unused',
      message: 'Concept `mater` is defined by `DEFI_MATERIAU` but never used.',
    },
  ],
};

function init(report: ValidationReport = REPORT) {
  window.dispatchEvent(
    new MessageEvent('message', {
      data: { command: 'init', report, commName: 'case.comm', exportName: 'case.export' },
    })
  );
}

describe('validation report webview', () => {
  it('shows a placeholder before the report arrives', () => {
    const { getByText } = render(App);
    expect(getByText(/Running validation/)).toBeTruthy();
  });

  it('renders both tables and the findings once initialised', async () => {
    const { getByText, getAllByText, getByLabelText } = render(App);
    init();
    // IMPR_RESU appears only in the command table; LIRE_MAILLAGE shows up in
    // both the command table and the I/O "Used in .comm" column.
    await waitFor(() => getByText('IMPR_RESU'));
    expect(getByText('Command / concept validity')).toBeTruthy();
    expect(getByText('I/O validity')).toBeTruthy();
    expect(getAllByText('LIRE_MAILLAGE').length).toBe(2);
    expect(getByText('mesh.med')).toBeTruthy();
    expect(getByText(/never used/)).toBeTruthy();
    // legend explains the glyphs in words
    expect(getByText(/not applicable/)).toBeTruthy();
    // the bottom bar reports the counts (1 warning in this fixture)
    expect(getByLabelText(/1 warning/i)).toBeTruthy();
  });

  it('shows an all-clear message in the bottom bar when there are no issues', async () => {
    const { getByText } = render(App);
    init({ ...REPORT, diagnostics: [] });
    await waitFor(() => getByText('No issues detected'));
  });

  it('skips the I/O table when there is no export', async () => {
    const { getByText } = render(App);
    init({ ...REPORT, hasExport: false, io: [] });
    await waitFor(() => getByText(/No associated .export file was found/));
  });
});
