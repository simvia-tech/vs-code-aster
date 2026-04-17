<script lang="ts">
  import AutocompleteInput from './AutocompleteInput.svelte';
  import {
    ALLOWED_TYPES,
    DEFAULT_UNITS,
    isInteger,
    getNextAvailableUnit,
    type AllowedType,
    type FileDescriptor,
  } from '../lib/types';

  interface Props {
    file: FileDescriptor;
    kind: 'input' | 'output';
    inputs: FileDescriptor[];
    outputs: FileDescriptor[];
    suggestionsFor: Record<string, string[]>;
    warningFor: Record<string, boolean>;
    onAutocompleteQuery: (id: string, value: string, type: string) => void;
    onAutocompleteFocus: (id: string | null) => void;
  }

  let {
    file = $bindable(),
    kind,
    inputs,
    outputs,
    suggestionsFor,
    warningFor,
    onAutocompleteQuery,
    onAutocompleteFocus,
  }: Props = $props();

  let unitInvalid = $derived(!isInteger(file.unit));
  let nameInvalid = $derived(warningFor[file.id] === true);

  function handleTypeChange() {
    const type = file.type as AllowedType;
    const def = DEFAULT_UNITS[type];
    if (def !== undefined) {
      file.unit = getNextAvailableUnit(def, inputs, outputs);
    }
  }

  function handleNameQuery(value: string) {
    file.name = value;
    onAutocompleteQuery(file.id, value, file.type);
  }
</script>

<div class="flex items-center gap-3">
  <select
    aria-label="File type"
    class="shrink-0 bg-ui-popup-bg text-ui-fg border border-ui-border rounded px-2 py-1 text-sm focus:border-ui-btn focus:outline-none"
    bind:value={file.type}
    onchange={handleTypeChange}
  >
    {#each ALLOWED_TYPES as t}
      <option value={t}>{t}</option>
    {/each}
  </select>

  {#if kind === 'input'}
    <AutocompleteInput
      id={`name-${file.id}`}
      bind:value={file.name}
      placeholder="File name"
      invalid={nameInvalid}
      suggestions={suggestionsFor[file.id] ?? []}
      onQuery={handleNameQuery}
      onFocusChange={(focused) => onAutocompleteFocus(focused ? file.id : null)}
    />
  {:else}
    <input
      id={`name-${file.id}`}
      type="text"
      aria-label="File name"
      class="flex-1 min-w-0 bg-ui-popup-bg text-ui-fg border border-ui-border rounded px-2 py-1 text-sm focus:border-ui-btn focus:outline-none"
      placeholder="File name"
      bind:value={file.name}
    />
  {/if}

  <input
    aria-label="Unit"
    type="text"
    class="w-20 shrink-0 bg-ui-popup-bg text-ui-fg border border-ui-border rounded px-2 py-1 text-sm focus:border-ui-btn focus:outline-none"
    class:input-warning={unitInvalid}
    bind:value={file.unit}
  />
</div>
