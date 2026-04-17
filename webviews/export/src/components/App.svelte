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
    name: 'simvia.export',
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

  // per-row autocomplete state
  let suggestionsFor = $state<Record<string, string[]>>({});
  let warningFor = $state<Record<string, boolean>>({});
  let lastQueriedId: string | null = null;

  // resources resolved by the extension (injected via message)
  let simviaLogoUrl = $state('');
  let simviaLogoDarkUrl = $state('');
  let asterLogoUrl = $state('');
  let asterLogoDarkUrl = $state('');

  let isValid = $derived(
    formData.name.trim().length > 0 &&
      Object.values(formData.parameters).every((v) => isInteger(v)) &&
      formData.inputFiles.every((f) => f.name.trim() !== '' && isInteger(f.unit)) &&
      formData.outputFiles.every((f) => f.name.trim() !== '' && isInteger(f.unit))
  );

  function makeFile(type = 'nom'): FileDescriptor {
    const unit = getNextAvailableUnit(
      DEFAULT_UNITS[type as keyof typeof DEFAULT_UNITS] ?? '0',
      formData.inputFiles,
      formData.outputFiles
    );
    return { id: newRowId(), type, name: '', unit };
  }

  function addInput() {
    formData.inputFiles.push(makeFile());
  }
  function removeInput() {
    const last = formData.inputFiles.pop();
    if (last) {
      delete suggestionsFor[last.id];
      delete warningFor[last.id];
    }
  }
  function addOutput() {
    formData.outputFiles.push(makeFile());
  }
  function removeOutput() {
    const last = formData.outputFiles.pop();
    if (last) {
      delete suggestionsFor[last.id];
      delete warningFor[last.id];
    }
  }

  function handleAutocompleteQuery(id: string, value: string, type: string) {
    lastQueriedId = id;
    vscode?.postMessage({ command: 'autocomplete', value, type });
  }

  function handleAutocompleteFocus(id: string | null) {
    if (id === null) {
      // closing suggestions for the focused row
      if (lastQueriedId) {
        suggestionsFor[lastQueriedId] = [];
      }
    }
  }

  function validate(): string {
    for (const [key, value] of Object.entries(formData.parameters)) {
      if (!isInteger(value)) {
        return `The parameter "${key}" must be an integer.`;
      }
    }

    const collectUnits = (files: FileDescriptor[]) => files.map((f) => String(f.unit));
    const inputUnits = collectUnits(formData.inputFiles);
    const outputUnits = collectUnits(formData.outputFiles);

    const checkFiles = (
      files: FileDescriptor[],
      label: 'Input' | 'Output',
      own: string[],
      other: string[]
    ): string => {
      for (let i = 0; i < files.length; i++) {
        const f = files[i];
        if (!f.name.trim()) {
          return `${label} file #${i + 1} is invalid: missing file name.`;
        }
        if (!isInteger(f.unit)) {
          return `${label} file #${i + 1} is invalid: unit must be an integer.`;
        }
        const unitStr = String(f.unit).trim();
        if (unitStr === '0') continue;
        const dupInOwn = own.filter((u, j) => j !== i && u === unitStr).length > 0;
        const dupInOther = other.includes(unitStr);
        if (dupInOwn || dupInOther) {
          return `${label} file #${i + 1} is invalid: ${unitStr} is already used as a unit value.`;
        }
      }
      return '';
    };

    const inputError = checkFiles(formData.inputFiles, 'Input', inputUnits, outputUnits);
    if (inputError) return inputError;
    const outputError = checkFiles(formData.outputFiles, 'Output', outputUnits, inputUnits);
    if (outputError) return outputError;

    return '';
  }

  function submit() {
    const error = validate();
    if (error) {
      vscode?.postMessage({ command: 'wrongCreation', value: error });
      return;
    }
    const lines: string[] = [];
    lines.push(formData.name.trim());
    for (const [key, value] of Object.entries(formData.parameters)) {
      lines.push(`P ${key} ${value.trim()}`);
    }
    for (const f of formData.inputFiles) {
      lines.push(`F ${f.type} ${f.name.trim()} D ${f.unit.trim()}`);
    }
    for (const f of formData.outputFiles) {
      lines.push(`F ${f.type} ${f.name.trim()} R ${f.unit.trim()}`);
    }
    vscode?.postMessage({ command: 'result', value: lines.join('\n') });
  }

  function cancel() {
    vscode?.postMessage({ command: 'cancel' });
  }

  onMount(() => {
    // seed with the same initial rows as the vanilla form (2 inputs + 1 output)
    formData.inputFiles.push(makeFile());
    formData.inputFiles.push(makeFile());
    formData.outputFiles.push(makeFile());

    window.addEventListener('message', handleMessage);
    vscode?.postMessage({ command: 'ready' });

    return () => window.removeEventListener('message', handleMessage);
  });

  function handleMessage(event: MessageEvent) {
    const message = event.data;
    if (!message || typeof message !== 'object') return;

    switch (message.command) {
      case 'assets': {
        simviaLogoUrl = message.simviaLogoUrl ?? '';
        simviaLogoDarkUrl = message.simviaLogoDarkUrl ?? '';
        asterLogoUrl = message.asterLogoUrl ?? '';
        asterLogoDarkUrl = message.asterLogoDarkUrl ?? '';
        break;
      }
      case 'exportFileAlreadyDefined': {
        applyExportFile(message.formData);
        break;
      }
      case 'autocompleteResult': {
        if (lastQueriedId) {
          suggestionsFor[lastQueriedId] = message.suggestions ?? [];
          warningFor[lastQueriedId] = false;
        }
        break;
      }
      case 'autocompleteFailed': {
        if (lastQueriedId) {
          suggestionsFor[lastQueriedId] = [];
          warningFor[lastQueriedId] = true;
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
    if (data.name) formData.name = data.name;
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

<main class="max-w-3xl mx-auto p-8 bg-ui-bg text-ui-fg">
  <Header {simviaLogoUrl} {simviaLogoDarkUrl} {asterLogoUrl} {asterLogoDarkUrl} />

  <div class="flex flex-col gap-2">
    <FieldRow id="envName" label="File name" bind:value={formData.name} />
    <FieldRow
      id="time_limit"
      label="Time Limit"
      kind="int"
      bind:value={formData.parameters.time_limit}
    />
    <FieldRow
      id="memory_limit"
      label="Memory Limit"
      kind="int"
      bind:value={formData.parameters.memory_limit}
    />
    <FieldRow id="ncpus" label="NCPUs" kind="int" bind:value={formData.parameters.ncpus} />
    <FieldRow
      id="mpi_nbcpu"
      label="MPI NBCPU"
      kind="int"
      bind:value={formData.parameters.mpi_nbcpu}
    />
    <FieldRow
      id="mpi_nbnoeud"
      label="MPI NBNOEUD"
      kind="int"
      bind:value={formData.parameters.mpi_nbnoeud}
    />
  </div>

  <FileSection
    title="Input Files"
    kind="input"
    bind:files={formData.inputFiles}
    inputs={formData.inputFiles}
    outputs={formData.outputFiles}
    {suggestionsFor}
    {warningFor}
    onAdd={addInput}
    onRemove={removeInput}
    onAutocompleteQuery={handleAutocompleteQuery}
    onAutocompleteFocus={handleAutocompleteFocus}
  />

  <FileSection
    title="Output Files"
    kind="output"
    bind:files={formData.outputFiles}
    inputs={formData.inputFiles}
    outputs={formData.outputFiles}
    {suggestionsFor}
    {warningFor}
    onAdd={addOutput}
    onRemove={removeOutput}
    onAutocompleteQuery={handleAutocompleteQuery}
    onAutocompleteFocus={handleAutocompleteFocus}
  />

  <SubmitBar canSubmit={isValid} onSubmit={submit} onCancel={cancel} />
</main>
