<script lang="ts">
  import { onMount } from 'svelte';
  import Header from './Header.svelte';
  import FieldRow from './FieldRow.svelte';
  import FileSection from './FileSection.svelte';
  import SubmitBar from './SubmitBar.svelte';
  import {
    DEFAULT_UNITS,
    getNextAvailableUnit,
    isInteger,
    newRowId,
    type FileDescriptor,
    type FormData,
  } from '../lib/types';

  interface VsCodeApi {
    postMessage(msg: unknown): void;
    getState(): unknown;
    setState(state: unknown): void;
  }

  let vscode: VsCodeApi | undefined;
  try {
    vscode = (window as unknown as { acquireVsCodeApi: () => VsCodeApi }).acquireVsCodeApi();
  } catch (e) {
    console.error('acquireVsCodeApi failed', e);
  }

  let formData = $state<FormData>({
    name: 'simvia',
    parameters: {
      time_limit: '300',
      memory_limit: '1024',
      ncpus: '1',
      mpi_nbcpu: '4',
      mpi_nbnoeud: '1',
    },
    inputFiles: [],
    outputFiles: [],
  });

  let suggestionsFor = $state<Record<string, string[]>>({});
  let lastQueriedId: string | null = null;

  // resources resolved by the extension (injected via message)
  let simviaLogoUrl = $state('');
  let simviaLogoDarkUrl = $state('');
  let asterLogoUrl = $state('');
  let asterLogoDarkUrl = $state('');
  let mode = $state<'create' | 'edit'>('create');
  let originalName = $state('');

  function isEmptyFile(f: FileDescriptor): boolean {
    return f.type.trim() === '' && f.name.trim() === '';
  }

  let errorFor = $derived.by(() => {
    const errors: Record<string, string> = {};

    if (formData.name.trim() === '') {
      errors['envName'] = 'The export file name is required.';
    }

    for (const [key, value] of Object.entries(formData.parameters)) {
      if (!isInteger(value)) {
        errors[key] = `"${key}" must be a whole number.`;
      }
    }

    const checkFiles = (files: FileDescriptor[], label: 'Input' | 'Output') => {
      files.forEach((f, idx) => {
        if (isEmptyFile(f)) {
          return;
        }
        const prefix = `${label} file #${idx + 1}`;
        const trimmedName = f.name.trim();
        const dotIdx = trimmedName.lastIndexOf('.');
        const base = dotIdx >= 0 ? trimmedName.slice(0, dotIdx) : trimmedName;
        const ext = dotIdx >= 0 ? trimmedName.slice(dotIdx + 1) : '';
        if (!f.type.trim()) {
          errors[`type-${f.id}`] = `${prefix}: file type is required.`;
        }
        if (!base) {
          errors[`name-${f.id}`] = `${prefix}: file name is required.`;
        }
        if (!ext) {
          errors[`ext-${f.id}`] = `${prefix}: file extension is required.`;
        }
        if (!isInteger(f.unit)) {
          errors[`unit-${f.id}`] = `${prefix}: unit must be a whole number.`;
        }
      });
    };
    checkFiles(formData.inputFiles, 'Input');
    checkFiles(formData.outputFiles, 'Output');

    return errors;
  });

  let formErrors = $derived.by(() => {
    const out: string[] = [];
    const hasComm = formData.inputFiles.some((f) => !isEmptyFile(f) && f.type === 'comm');
    if (!hasComm) {
      out.push('At least one comm input file is required.');
    }
    return out;
  });

  let allErrors = $derived<{ targetId?: string; message: string }[]>([
    ...Object.entries(errorFor).map(([targetId, message]) => ({ targetId, message })),
    ...formErrors.map((message) => ({ message })),
  ]);

  function focusTarget(id: string) {
    const el = document.getElementById(id);
    if (!el) {
      return;
    }
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    (el as HTMLElement).focus({ preventScroll: true });
  }

  let warnings = $derived.by(() => {
    const out: { targetId?: string; message: string }[] = [];

    if (
      mode === 'edit' &&
      originalName &&
      formData.name.trim() &&
      formData.name.trim() !== originalName
    ) {
      out.push({
        targetId: 'envName',
        message: `Saving will rename ${originalName}.export to ${formData.name.trim()}.export. The original file will be deleted.`,
      });
    }

    const meshTypes = new Set(['mmed', 'mail', 'msh']);
    const hasMesh = [...formData.inputFiles, ...formData.outputFiles].some(
      (f) => !isEmptyFile(f) && meshTypes.has(f.type)
    );
    if (!hasMesh) {
      out.push({
        targetId: 'add-input',
        message: 'No mesh file is set (mmed, mail, or msh).',
      });
    }

    const hasRmed = formData.outputFiles.some((f) => !isEmptyFile(f) && f.type === 'rmed');
    if (!hasRmed) {
      out.push({
        targetId: 'add-output',
        message: 'No rmed output file is set.',
      });
    }

    const byUnit = new Map<string, { names: string[]; firstId: string }>();
    for (const f of [...formData.inputFiles, ...formData.outputFiles]) {
      if (isEmptyFile(f)) {
        continue;
      }
      if (!isInteger(f.unit)) {
        continue;
      }
      const unitStr = String(f.unit).trim();
      if (unitStr === '0') {
        continue;
      }
      const label = f.name.trim() || `(unnamed ${f.type || 'file'})`;
      const existing = byUnit.get(unitStr);
      if (existing) {
        existing.names.push(label);
      } else {
        byUnit.set(unitStr, { names: [label], firstId: f.id });
      }
    }
    for (const [unit, { names, firstId }] of byUnit) {
      if (names.length > 1) {
        out.push({
          targetId: `unit-${firstId}`,
          message: `Multiple files share unit ${unit}: ${names.join(', ')}`,
        });
      }
    }
    return out;
  });

  let isValid = $derived(Object.keys(errorFor).length === 0 && formErrors.length === 0);

  function makeFile(type = ''): FileDescriptor {
    const unit = type
      ? getNextAvailableUnit(type, [...formData.inputFiles, ...formData.outputFiles])
      : '0';
    return { id: newRowId(), type, name: '', unit };
  }

  function addInput() {
    formData.inputFiles.push(makeFile());
  }
  function addOutput() {
    formData.outputFiles.push(makeFile());
  }

  function removeFile(id: string) {
    let idx = formData.inputFiles.findIndex((f) => f.id === id);
    if (idx >= 0) {
      formData.inputFiles.splice(idx, 1);
    } else {
      idx = formData.outputFiles.findIndex((f) => f.id === id);
      if (idx >= 0) {
        formData.outputFiles.splice(idx, 1);
      }
    }
    delete suggestionsFor[id];
  }

  function handleAutocompleteQuery(id: string, value: string, type: string) {
    lastQueriedId = id;
    vscode?.postMessage({ command: 'autocomplete', value, type });
  }

  function handleAutocompleteFocus(id: string | null) {
    if (id === null && lastQueriedId) {
      suggestionsFor[lastQueriedId] = [];
    }
  }

  function submit() {
    if (!isValid) {
      const first = Object.keys(errorFor)[0];
      document.getElementById(first)?.focus();
      return;
    }
    const lines: string[] = [];
    lines.push(`${formData.name.trim()}.export`);
    for (const [key, value] of Object.entries(formData.parameters)) {
      lines.push(`P ${key} ${value.trim()}`);
    }
    for (const f of formData.inputFiles) {
      if (isEmptyFile(f)) {
        continue;
      }
      const head = f.type === 'base' ? 'R' : 'F';
      const status = f.type === 'base' ? 'DC' : 'D';
      lines.push(`${head} ${f.type} ${f.name.trim()} ${status} ${f.unit.trim()}`);
    }
    for (const f of formData.outputFiles) {
      if (isEmptyFile(f)) {
        continue;
      }
      const head = f.type === 'base' ? 'R' : 'F';
      const status = f.type === 'base' ? 'RC' : 'R';
      lines.push(`${head} ${f.type} ${f.name.trim()} ${status} ${f.unit.trim()}`);
    }
    vscode?.postMessage({ command: 'result', value: lines.join('\n') });
  }

  function cancel() {
    vscode?.postMessage({ command: 'cancel' });
  }

  function scrollTo(id: string) {
    const el = document.getElementById(id);
    if (!el) {
      return;
    }
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  let initialized = false;
  let loadedFromState = false;

  onMount(() => {
    const saved = vscode?.getState() as { formData?: FormData } | undefined;
    if (saved?.formData) {
      Object.assign(formData, saved.formData);
      loadedFromState = true;
    } else {
      formData.inputFiles.push({
        id: newRowId(),
        type: 'comm',
        name: 'simvia.comm',
        unit: DEFAULT_UNITS.comm,
      });
      formData.inputFiles.push({
        id: newRowId(),
        type: 'mmed',
        name: 'simvia.mmed',
        unit: DEFAULT_UNITS.mmed,
      });
      formData.outputFiles.push({
        id: newRowId(),
        type: 'rmed',
        name: 'simvia.rmed',
        unit: DEFAULT_UNITS.rmed,
      });
    }

    window.addEventListener('message', handleMessage);
    vscode?.postMessage({ command: 'ready' });
    initialized = true;

    return () => window.removeEventListener('message', handleMessage);
  });

  $effect(() => {
    if (!initialized) {
      return;
    }
    vscode?.setState({ formData: $state.snapshot(formData) });
  });

  $effect(() => {
    if (!initialized) {
      return;
    }
    vscode?.postMessage({ command: 'titleChange', name: formData.name.trim() });
  });

  function handleMessage(event: MessageEvent) {
    const message = event.data;
    if (!message || typeof message !== 'object') {
      return;
    }

    switch (message.command) {
      case 'assets': {
        simviaLogoUrl = message.simviaLogoUrl ?? '';
        simviaLogoDarkUrl = message.simviaLogoDarkUrl ?? '';
        asterLogoUrl = message.asterLogoUrl ?? '';
        asterLogoDarkUrl = message.asterLogoDarkUrl ?? '';
        if (message.mode === 'edit' || message.mode === 'create') {
          mode = message.mode;
        }
        if (typeof message.originalName === 'string') {
          originalName = message.originalName;
        }
        break;
      }
      case 'exportFileAlreadyDefined': {
        if (!loadedFromState) {
          applyExportFile(message.formData);
        }
        break;
      }
      case 'autocompleteResult': {
        if (lastQueriedId) {
          suggestionsFor[lastQueriedId] = message.suggestions ?? [];
        }
        break;
      }
      case 'autocompleteFailed': {
        if (lastQueriedId) {
          suggestionsFor[lastQueriedId] = [];
        }
        break;
      }
    }
  }

  function applyExportFile(data: {
    name: string;
    parameters: Record<string, string>;
    inputFiles: Array<{ type: string; name: string; unit: string }>;
    outputFiles: Array<{ type: string; name: string; unit: string }>;
  }) {
    if (data.name) {
      formData.name = data.name.replace(/\.export$/i, '');
    }
    if (data.parameters) {
      const params = formData.parameters as unknown as Record<string, string>;
      for (const key of Object.keys(params)) {
        const v = data.parameters[key];
        if (v !== undefined && v !== '') {
          params[key] = v;
        }
      }
    }
    if (
      (data.inputFiles && data.inputFiles.length > 0) ||
      (data.outputFiles && data.outputFiles.length > 0)
    ) {
      formData.inputFiles = (data.inputFiles ?? []).map((f) => ({
        id: newRowId(),
        type: f.type,
        name: f.name,
        unit: String(f.unit),
      }));
      formData.outputFiles = (data.outputFiles ?? []).map((f) => ({
        id: newRowId(),
        type: f.type,
        name: f.name,
        unit: String(f.unit),
      }));
    }
  }
</script>

<main class="max-w-3xl mx-auto p-8 bg-ui-bg text-ui-fg min-h-screen flex flex-col">
  <Header
    title={mode === 'edit' ? 'Edit an export file' : 'Create a new export file'}
    {simviaLogoUrl}
    {simviaLogoDarkUrl}
    {asterLogoUrl}
    {asterLogoDarkUrl}
  />

  <div class="mb-6">
    <FieldRow
      id="envName"
      label="File name"
      accent
      suffix=".export"
      bind:value={formData.name}
      error={errorFor['envName']}
    />
  </div>

  <div class="grid grid-cols-2 gap-x-6 gap-y-2 mt-2">
    <FieldRow
      id="time_limit"
      label="Time Limit"
      kind="int"
      bind:value={formData.parameters.time_limit}
      error={errorFor['time_limit']}
    />
    <FieldRow
      id="ncpus"
      label="NCPUs"
      kind="int"
      bind:value={formData.parameters.ncpus}
      error={errorFor['ncpus']}
    />
    <FieldRow
      id="memory_limit"
      label="Memory Limit"
      kind="int"
      bind:value={formData.parameters.memory_limit}
      error={errorFor['memory_limit']}
    />
    <FieldRow
      id="mpi_nbcpu"
      label="MPI NBCPU"
      kind="int"
      bind:value={formData.parameters.mpi_nbcpu}
      error={errorFor['mpi_nbcpu']}
    />
    <div class="col-start-2">
      <FieldRow
        id="mpi_nbnoeud"
        label="MPI NBNOEUD"
        kind="int"
        bind:value={formData.parameters.mpi_nbnoeud}
        error={errorFor['mpi_nbnoeud']}
      />
    </div>
  </div>

  <FileSection
    title="Input Files"
    kind="input"
    bind:files={formData.inputFiles}
    inputs={formData.inputFiles}
    outputs={formData.outputFiles}
    {suggestionsFor}
    {errorFor}
    onAdd={addInput}
    onAutocompleteQuery={handleAutocompleteQuery}
    onAutocompleteFocus={handleAutocompleteFocus}
    onRemove={removeFile}
  />

  <FileSection
    title="Output Files"
    kind="output"
    bind:files={formData.outputFiles}
    inputs={formData.inputFiles}
    outputs={formData.outputFiles}
    {suggestionsFor}
    {errorFor}
    onAdd={addOutput}
    onAutocompleteQuery={handleAutocompleteQuery}
    onAutocompleteFocus={handleAutocompleteFocus}
    onRemove={removeFile}
  />

  {#if allErrors.length > 0}
    <div
      id="panel-errors"
      class="panel-errors mt-6 p-4 rounded border text-sm scroll-mt-8 scroll-mb-20"
      style="border-color: var(--vscode-inputValidation-errorBorder, #d45858); background: color-mix(in srgb, var(--vscode-inputValidation-errorBorder, #d45858) 12%, transparent); color: var(--vscode-inputValidation-errorBorder, #d45858)"
      role="alert"
    >
      <div class="font-semibold mb-3">
        {allErrors.length === 1 ? 'Error' : 'Errors'}
      </div>
      <ul class="flex flex-col gap-0.5">
        {#each allErrors as e}
          <li>
            <button
              type="button"
              class="panel-row w-full text-left flex items-start gap-2 py-1 px-2 -mx-1 rounded {e.targetId
                ? 'cursor-pointer'
                : 'cursor-default'}"
              disabled={!e.targetId}
              onclick={() => e.targetId && focusTarget(e.targetId)}
            >
              <svg
                class="shrink-0 mt-0.5"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>{e.message}</span>
            </button>
          </li>
        {/each}
      </ul>
    </div>
  {/if}

  {#if warnings.length > 0}
    <div
      id="panel-warnings"
      class="panel-warnings mt-6 p-4 rounded border text-sm scroll-mt-8 scroll-mb-20"
      style="border-color: var(--vscode-editorWarning-foreground, #cca700); background: color-mix(in srgb, var(--vscode-editorWarning-foreground, #cca700) 10%, transparent); color: var(--vscode-editorWarning-foreground, #cca700)"
      role="alert"
    >
      <div class="font-semibold mb-3">
        {warnings.length === 1 ? 'Warning' : 'Warnings'}
      </div>
      <ul class="flex flex-col gap-0.5">
        {#each warnings as w}
          <li>
            <button
              type="button"
              class="panel-row w-full text-left flex items-start gap-2 py-1 px-2 -mx-1 rounded {w.targetId
                ? 'cursor-pointer'
                : 'cursor-default'}"
              disabled={!w.targetId}
              onclick={() => w.targetId && focusTarget(w.targetId)}
            >
              <svg
                class="shrink-0 mt-0.5"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path
                  d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"
                />
                <path d="M12 9v4" />
                <path d="M12 17h.01" />
              </svg>
              <span>{w.message}</span>
            </button>
          </li>
        {/each}
      </ul>
    </div>
  {/if}

  <div class="pb-8"></div>

  <SubmitBar
    canSubmit={isValid}
    submitLabel={mode === 'edit' ? 'Save' : 'Create'}
    errorCount={Object.keys(errorFor).length + formErrors.length}
    warningCount={warnings.length}
    onSubmit={submit}
    onCancel={cancel}
    onScrollToErrors={() => scrollTo('panel-errors')}
    onScrollToWarnings={() => scrollTo('panel-warnings')}
  />
</main>

<style>
  .panel-errors .panel-row:not(:disabled):hover {
    background: color-mix(
      in srgb,
      var(--vscode-inputValidation-errorBorder, #d45858) 18%,
      transparent
    );
  }
  .panel-warnings .panel-row:not(:disabled):hover {
    background: color-mix(
      in srgb,
      var(--vscode-editorWarning-foreground, #cca700) 18%,
      transparent
    );
  }
</style>
