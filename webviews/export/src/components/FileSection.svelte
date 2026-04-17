<script lang="ts">
  import FileRow from './FileRow.svelte';
  import type { FileDescriptor } from '../lib/types';

  interface Props {
    title: string;
    kind: 'input' | 'output';
    files: FileDescriptor[];
    inputs: FileDescriptor[];
    outputs: FileDescriptor[];
    suggestionsFor: Record<string, string[]>;
    warningFor: Record<string, boolean>;
    onAdd: () => void;
    onRemove: () => void;
    onAutocompleteQuery: (id: string, value: string, type: string) => void;
    onAutocompleteFocus: (id: string | null) => void;
  }

  let {
    title,
    kind,
    files = $bindable(),
    inputs,
    outputs,
    suggestionsFor,
    warningFor,
    onAdd,
    onRemove,
    onAutocompleteQuery,
    onAutocompleteFocus,
  }: Props = $props();
</script>

<section class="mt-6">
  <div class="flex items-center gap-2 mb-2">
    <h2 class="text-base font-semibold text-ui-text-primary">{title}</h2>
    <button
      type="button"
      class="w-7 h-7 flex items-center justify-center rounded bg-ui-elem hover:bg-ui-elem-hover text-ui-fg text-base leading-none"
      aria-label={`Add ${title.toLowerCase()}`}
      onclick={onAdd}>+</button
    >
    <button
      type="button"
      class="w-7 h-7 flex items-center justify-center rounded bg-ui-elem hover:bg-ui-elem-hover text-ui-fg text-base leading-none disabled:opacity-40 disabled:cursor-not-allowed"
      aria-label={`Remove ${title.toLowerCase()}`}
      disabled={files.length === 0}
      onclick={onRemove}>−</button
    >
  </div>

  <div class="flex flex-col gap-2">
    {#each files as _file, i (files[i].id)}
      <FileRow
        bind:file={files[i]}
        {kind}
        {inputs}
        {outputs}
        {suggestionsFor}
        {warningFor}
        {onAutocompleteQuery}
        {onAutocompleteFocus}
      />
    {/each}
  </div>
</section>
