<script lang="ts">
  import { dndzone, type DndEvent } from 'svelte-dnd-action';
  import { flip } from 'svelte/animate';
  import FileRow from './FileRow.svelte';
  import type { FileDescriptor } from '../lib/types';

  interface Props {
    title: string;
    kind: 'input' | 'output';
    files: FileDescriptor[];
    inputs: FileDescriptor[];
    outputs: FileDescriptor[];
    suggestionsFor: Record<string, string[]>;
    errorFor: Record<string, string>;
    onAdd: () => void;
    onAutocompleteQuery: (id: string, value: string, type: string) => void;
    onAutocompleteFocus: (id: string | null) => void;
    onRemove: (id: string) => void;
  }

  let {
    title,
    kind,
    files = $bindable(),
    inputs,
    outputs,
    suggestionsFor,
    errorFor,
    onAdd,
    onAutocompleteQuery,
    onAutocompleteFocus,
    onRemove,
  }: Props = $props();

  const FLIP_MS = 180;

  function handleConsider(e: CustomEvent<DndEvent<FileDescriptor>>) {
    files = e.detail.items;
  }

  function handleFinalize(e: CustomEvent<DndEvent<FileDescriptor>>) {
    files = e.detail.items;
  }
</script>

<section class="mt-6">
  <h2 class="text-base font-semibold text-ui-text-primary mb-2">{title}</h2>

  <div
    class="flex flex-col gap-2"
    use:dndzone={{
      items: files,
      flipDurationMs: FLIP_MS,
      dropTargetStyle: {
        outline: '2px dashed var(--ui-focus)',
        outlineOffset: '2px',
        borderRadius: '4px',
      },
      type: `file-${kind}`,
      dragDisabled: false,
    }}
    onconsider={handleConsider}
    onfinalize={handleFinalize}
  >
    {#each files as _file, i (files[i].id)}
      <div animate:flip={{ duration: FLIP_MS }}>
        <FileRow
          bind:file={files[i]}
          {kind}
          {inputs}
          {outputs}
          {suggestionsFor}
          {errorFor}
          {onAutocompleteQuery}
          {onAutocompleteFocus}
          {onRemove}
        />
      </div>
    {/each}
  </div>

  <button
    id={`add-${kind}`}
    type="button"
    class="w-full mt-3 flex items-center justify-center gap-1.5 py-1.5 rounded border border-dashed border-ui-border text-xs font-medium text-ui-text-secondary hover:text-ui-fg hover:bg-ui-elem hover:border-ui-text-muted cursor-pointer transition-colors"
    aria-label={`Add ${kind} file`}
    onclick={onAdd}
  >
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      stroke="currentColor"
      stroke-width="1.6"
      stroke-linecap="round"
      aria-hidden="true"
    >
      <path d="M6 1.5 V10.5 M1.5 6 H10.5" />
    </svg>
    Add {kind} file
  </button>
</section>
