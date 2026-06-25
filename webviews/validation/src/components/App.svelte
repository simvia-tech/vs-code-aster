<script lang="ts">
  import { onMount } from 'svelte';
  import Header from '../../../shared/components/Header.svelte';
  import SubmitBar from '../../../shared/components/SubmitBar.svelte';
  import {
    type ValidationReport,
    type CheckResult,
    type IoRow,
    checkGlyph,
    ioGlyph,
    severityGlyph,
    countDiagnostics,
    GLYPH_LEGEND,
    CHECK_DOCS,
  } from '@report';

  interface VsCodeApi {
    postMessage(msg: unknown): void;
  }
  let vscode: VsCodeApi | undefined;
  try {
    vscode = (window as unknown as { acquireVsCodeApi: () => VsCodeApi }).acquireVsCodeApi();
  } catch (e) {
    console.error('acquireVsCodeApi failed', e);
  }

  let report = $state<ValidationReport | null>(null);
  let commName = $state('');
  let exportName = $state('');
  let simviaLogoUrl = $state('');
  let simviaLogoDarkUrl = $state('');
  let asterLogoUrl = $state('');
  let asterLogoDarkUrl = $state('');

  const counts = $derived(report ? countDiagnostics(report) : { errors: 0, warnings: 0 });

  let findingsEl = $state<HTMLElement | undefined>(undefined);
  function scrollToFindings() {
    findingsEl?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  interface InitMessage {
    command: string;
    report?: ValidationReport;
    commName?: string;
    exportName?: string;
    simviaLogoUrl?: string;
    simviaLogoDarkUrl?: string;
    asterLogoUrl?: string;
    asterLogoDarkUrl?: string;
  }

  function handleMessage(msg: InitMessage) {
    if (msg.command !== 'init') {
      return;
    }
    report = msg.report ?? null;
    commName = msg.commName ?? '';
    exportName = msg.exportName ?? '';
    simviaLogoUrl = msg.simviaLogoUrl ?? '';
    simviaLogoDarkUrl = msg.simviaLogoDarkUrl ?? '';
    asterLogoUrl = msg.asterLogoUrl ?? '';
    asterLogoDarkUrl = msg.asterLogoDarkUrl ?? '';
  }

  onMount(() => {
    const handler = (e: MessageEvent) => handleMessage(e.data);
    window.addEventListener('message', handler);
    vscode?.postMessage({ command: 'ready' });
    return () => window.removeEventListener('message', handler);
  });

  function jump(file: 'comm' | 'export', line: number) {
    vscode?.postMessage({ command: 'jump', file, line });
  }

  function jumpKey(e: KeyboardEvent, file: 'comm' | 'export', line: number) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      jump(file, line);
    }
  }

  const cell = (v: CheckResult, advisory = false) => checkGlyph(v, advisory);
  const ioStatusLabel = (s: IoRow['status']) =>
    s === 'ok' ? 'consistent' : s === 'warning' ? 'warning' : 'problem';

  const severityOrder = (s: 'error' | 'warning' | 'information') =>
    s === 'error' ? 0 : s === 'warning' ? 1 : 2;
</script>

<main class="p-8 min-h-screen flex flex-col">
  <Header
    title="Study validation"
    {simviaLogoUrl}
    {simviaLogoDarkUrl}
    {asterLogoUrl}
    {asterLogoDarkUrl}
    compact
  />

  {#if report}
    <div class="flex-1 pb-8">
    <div class="text-sm text-ui-text-secondary mb-1">
      Command file:
      <button class="filelink" onclick={() => jump('comm', 0)}>{commName}</button>
      {#if report.hasExport}
        · Export: <button class="filelink" onclick={() => jump('export', 0)}>{exportName}</button>
      {:else}
        · <span class="text-ui-text-muted">no .export file found — I/O checks skipped</span>
      {/if}
    </div>

    <ul class="legend">
      {#each GLYPH_LEGEND as item}
        <li><span class="glyph">{item.glyph}</span> {item.text}</li>
      {/each}
    </ul>

    <h2>
      Command / concept validity
      <span class="subtle">hover a column header for what it checks</span>
    </h2>
    <div class="overflow-x-auto">
      <table>
        <thead>
          <tr>
            <th>Concept</th>
            <th>Command</th>
            <th class="center" title={CHECK_DOCS.syntactic}>Syntactic</th>
            <th class="center" title={CHECK_DOCS.dependency}>Dependency</th>
            <th class="center" title={CHECK_DOCS.naming}>Naming</th>
            <th class="center" title={CHECK_DOCS.used}>Used</th>
          </tr>
        </thead>
        <tbody>
          {#if report.commands.length === 0}
            <tr><td colspan="6" class="empty">No commands found in the command file.</td></tr>
          {:else}
            {#each report.commands as row}
              <!-- Row click is a convenience shortcut; the same jump is fully
                   keyboard-accessible via the Findings buttons and file links. -->
              <!-- svelte-ignore a11y_no_noninteractive_element_interactions a11y_no_noninteractive_element_to_interactive_role -->
              <tr
                class="jump"
                role="button"
                tabindex="0"
                onclick={() => jump('comm', row.line)}
                onkeydown={(e) => jumpKey(e, 'comm', row.line)}
              >
                <td>
                  {#if row.concept === '[noname]'}
                    <span class="text-ui-text-muted">[noname]</span>
                  {:else}
                    {row.concept}
                  {/if}
                </td>
                <td class="mono">{row.command}</td>
                <td class="center" title={CHECK_DOCS.syntactic}>{cell(row.syntactic)}</td>
                <td class="center" title={CHECK_DOCS.dependency}>{cell(row.dependency)}</td>
                <td class="center" title={CHECK_DOCS.naming}>{cell(row.naming, true)}</td>
                <td class="center" title={CHECK_DOCS.used}>{cell(row.used, true)}</td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>

    <h2>I/O validity <span class="subtle">.comm ↔ .export units</span></h2>
    {#if report.hasExport}
      <div class="overflow-x-auto">
        <table>
          <thead>
            <tr>
              <th>Unit</th>
              <th>Direction</th>
              <th>File</th>
              <th>Export type</th>
              <th>Used in .comm</th>
              <th class="center">Status</th>
            </tr>
          </thead>
          <tbody>
            {#if report.io.length === 0}
              <tr><td colspan="6" class="empty">No logical units found.</td></tr>
            {:else}
              {#each report.io as r}
                <tr>
                  <td class="mono">{r.unit}</td>
                  <td>{r.direction}</td>
                  <td class="mono">{r.file}</td>
                  <td class="mono">{r.exportType}</td>
                  <td class="mono">{r.usedIn}</td>
                  <td class="center" title={ioStatusLabel(r.status)}>{ioGlyph(r.status)}</td>
                </tr>
              {/each}
            {/if}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="text-ui-text-muted">
        No associated .export file was found, so unit consistency was not checked.
      </p>
    {/if}

    {#if report.diagnostics.length > 0}
      <div bind:this={findingsEl}>
        <h2>Findings <span class="subtle">click to jump to the source</span></h2>
        <div class="findings">
        {#each [...report.diagnostics].sort((a, b) => severityOrder(a.severity) - severityOrder(b.severity) || a.line - b.line) as d}
          <button class="finding" onclick={() => jump(d.file, d.line)}>
            <span class="glyph">{severityGlyph(d.severity)}</span>
            {d.message}
            <span class="text-ui-text-muted">({d.file})</span>
          </button>
        {/each}
        </div>
      </div>
    {/if}
    </div>

    <SubmitBar
      sticky
      errorCount={counts.errors}
      warningCount={counts.warnings}
      okMessage="No issues detected"
      onScrollToErrors={scrollToFindings}
      onScrollToWarnings={scrollToFindings}
    />
  {:else}
    <p class="text-ui-text-muted mt-4">Running validation…</p>
  {/if}
</main>

<style>
  h2 {
    font-size: 1.05em;
    margin: 24px 0 8px;
    border-bottom: 1px solid var(--ui-border);
    padding-bottom: 4px;
    color: var(--ui-text-primary);
  }
  .subtle {
    color: var(--ui-text-muted);
    font-size: 0.85em;
    font-weight: normal;
    margin-left: 6px;
  }
  table {
    border-collapse: collapse;
    width: 100%;
  }
  th,
  td {
    text-align: left;
    padding: 4px 10px;
    border-bottom: 1px solid var(--ui-border);
  }
  th {
    color: var(--ui-text-secondary);
    font-weight: 600;
  }
  th[title] {
    text-decoration: underline dotted;
    text-underline-offset: 3px;
    cursor: help;
  }
  td[title] {
    cursor: help;
  }
  .center {
    text-align: center;
  }
  .mono {
    font-family: var(--vscode-editor-font-family, monospace);
  }
  tr.jump {
    cursor: pointer;
  }
  tr.jump:hover td {
    background: var(--ui-element-bg);
  }
  td.empty {
    color: var(--ui-text-muted);
    font-style: italic;
    text-align: center;
  }
  .filelink {
    color: var(--ui-link);
    text-decoration: underline;
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
    font: inherit;
  }
  ul.legend {
    list-style: none;
    padding: 0;
    color: var(--ui-text-muted);
    font-size: 0.9em;
    margin: 4px 0 8px;
  }
  ul.legend li {
    padding: 1px 0;
  }
  ul.legend .glyph,
  .findings .glyph {
    display: inline-block;
    width: 1.4em;
  }
  .findings {
    margin: 4px 0;
  }
  .findings button {
    display: block;
    width: 100%;
    text-align: left;
    padding: 4px 6px;
    border: none;
    border-bottom: 1px solid var(--ui-border);
    background: none;
    color: inherit;
    font: inherit;
    cursor: pointer;
  }
  .findings button:hover {
    background: var(--ui-element-bg);
  }
</style>
