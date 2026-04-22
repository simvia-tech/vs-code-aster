<script lang="ts">
  import AutocompleteInput from './AutocompleteInput.svelte';
  import Dropdown from './ui/Dropdown.svelte';
  import {
    INPUT_TYPES,
    OUTPUT_TYPES,
    getNextAvailableUnit,
    isFixedZeroType,
    isInteger,
    type FileDescriptor,
  } from '../lib/types';

  interface Props {
    file: FileDescriptor;
    kind: 'input' | 'output';
    inputs: FileDescriptor[];
    outputs: FileDescriptor[];
    suggestionsFor: Record<string, string[]>;
    errorFor: Record<string, string>;
    onAutocompleteQuery: (id: string, value: string, type: string) => void;
    onAutocompleteFocus: (id: string | null) => void;
    onRemove: (id: string) => void;
  }

  let {
    file = $bindable(),
    kind,
    inputs,
    outputs,
    suggestionsFor,
    errorFor,
    onAutocompleteQuery,
    onAutocompleteFocus,
    onRemove,
  }: Props = $props();

  let nameError = $derived(errorFor[`name-${file.id}`] ?? '');
  let extError = $derived(errorFor[`ext-${file.id}`] ?? '');
  let unitError = $derived(errorFor[`unit-${file.id}`] ?? '');
  let typeError = $derived(errorFor[`type-${file.id}`] ?? '');
  let rowErrors = $derived([typeError, nameError, extError, unitError].filter((m) => m !== ''));

  let typeOptions = $derived(
    (kind === 'input' ? INPUT_TYPES : OUTPUT_TYPES).map((t) => ({ value: t, label: t }))
  );

  let unitLocked = $derived(isFixedZeroType(file.type));

  function splitName(name: string): { base: string; ext: string } {
    const idx = name.lastIndexOf('.');
    if (idx < 0) {
      return { base: name, ext: '' };
    }
    return { base: name.slice(0, idx), ext: name.slice(idx + 1) };
  }

  let baseName = $state(splitName(file.name).base);
  let extension = $state(splitName(file.name).ext);

  $effect(() => {
    const composed = extension ? `${baseName}.${extension}` : baseName;
    if (composed !== file.name) {
      file.name = composed;
    }
  });

  function handleTypeChange(newType: string) {
    if (file.type === newType) {
      return;
    }
    const previousType = file.type;
    if (extension === '' || extension === previousType) {
      extension = newType;
    }
    file.type = newType;
    if (isFixedZeroType(newType)) {
      file.unit = '0';
      return;
    }
    file.unit = getNextAvailableUnit(newType, [...inputs, ...outputs], file.id);
  }

  function handleUnitKeydown(e: KeyboardEvent) {
    if (unitLocked) {
      return;
    }
    if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') {
      return;
    }
    if (!isInteger(file.unit)) {
      return;
    }
    e.preventDefault();
    const n = Number(file.unit) + (e.key === 'ArrowUp' ? 1 : -1);
    file.unit = String(Math.max(0, n));
  }

  function handleNameQuery(value: string) {
    // Suggestions are full filenames ("simvia.comm"); if a dot is present,
    // split it so the two fields stay coherent.
    const { base, ext } = splitName(value);
    if (ext) {
      baseName = base;
      extension = ext;
    } else {
      baseName = value;
    }
    onAutocompleteQuery(file.id, value, file.type);
  }
</script>

<div class="flex flex-col gap-1">
  <div class="relative flex items-center gap-2 rounded">
    <span
      class="shrink-0 text-ui-text-muted hover:text-ui-fg cursor-grab active:cursor-grabbing px-1 py-1 rounded hover:bg-ui-elem touch-none select-none"
      aria-label="Drag to reorder"
      role="button"
      tabindex="-1"
    >
      <svg width="12" height="16" viewBox="0 0 12 16" fill="currentColor" aria-hidden="true">
        <circle cx="3" cy="3" r="1.2" />
        <circle cx="9" cy="3" r="1.2" />
        <circle cx="3" cy="8" r="1.2" />
        <circle cx="9" cy="8" r="1.2" />
        <circle cx="3" cy="13" r="1.2" />
        <circle cx="9" cy="13" r="1.2" />
      </svg>
    </span>

    <Dropdown options={typeOptions} value={file.type || null} onSelect={handleTypeChange}>
      <button
        type="button"
        class="shrink-0 flex items-center gap-1 bg-ui-input-bg border border-ui-input-border rounded-sm px-2 py-1 text-sm cursor-pointer focus:border-ui-focus focus:outline-none w-24 justify-between {file.type
          ? 'text-ui-input-fg'
          : 'text-ui-text-muted italic'}"
        class:input-warning={!!typeError}
        aria-label="File type"
      >
        <span>{file.type || 'Type'}</span>
        <svg width="8" height="8" viewBox="0 0 8 8" fill="currentColor" aria-hidden="true">
          <path d="M1 2.5 L4 5.5 L7 2.5 Z" />
        </svg>
      </button>
    </Dropdown>

    <AutocompleteInput
      id={`name-${file.id}`}
      bind:value={baseName}
      placeholder="File name"
      invalid={!!nameError}
      suggestions={suggestionsFor[file.id] ?? []}
      onQuery={handleNameQuery}
      onFocusChange={(focused) => onAutocompleteFocus(focused ? file.id : null)}
    />

    <span class="text-ui-text-muted select-none">.</span>

    <input
      id={`ext-${file.id}`}
      aria-label="File extension"
      type="text"
      class="w-20 shrink-0 bg-ui-input-bg border border-ui-input-border rounded-sm px-2 py-1 text-sm text-ui-input-fg focus:border-ui-focus focus:outline-none"
      class:input-warning={!!extError}
      placeholder="ext"
      bind:value={extension}
    />

    <input
      id={`unit-${file.id}`}
      aria-label="Unit"
      type="text"
      class="w-16 shrink-0 bg-ui-input-bg border border-ui-input-border rounded-sm px-2 py-1 text-sm focus:border-ui-focus focus:outline-none {unitLocked
        ? 'text-ui-text-muted cursor-not-allowed'
        : 'text-ui-input-fg'}"
      class:input-warning={!!unitError}
      bind:value={file.unit}
      readonly={unitLocked}
      tabindex={unitLocked ? -1 : 0}
      onkeydown={handleUnitKeydown}
    />

    <button
      type="button"
      class="shrink-0 w-6 h-6 flex items-center justify-center rounded text-ui-text-muted hover:text-ui-fg hover:bg-ui-elem-hover cursor-pointer"
      aria-label="Remove file"
      onclick={() => onRemove(file.id)}
    >
      <svg
        width="10"
        height="10"
        viewBox="0 0 10 10"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        aria-hidden="true"
      >
        <path d="M2 2 L8 8 M8 2 L2 8" />
      </svg>
    </button>
  </div>

  {#if rowErrors.length > 0}
    <ul
      class="px-7 text-xs flex flex-col gap-0.5"
      style="color: var(--vscode-inputValidation-errorBorder, #d45858)"
    >
      {#each rowErrors as message}
        <li>{message}</li>
      {/each}
    </ul>
  {/if}
</div>
