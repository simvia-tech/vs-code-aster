<script lang="ts">
  import { isInteger } from '../lib/types';

  interface Props {
    id: string;
    label: string;
    value: string;
    kind?: 'text' | 'int';
    placeholder?: string;
  }

  let { id, label, value = $bindable(), kind = 'text', placeholder = '' }: Props = $props();

  let invalid = $derived(kind === 'int' && !isInteger(value));
</script>

<div class="flex items-center gap-3 bg-ui-elem rounded-md px-3 py-2">
  <label for={id} class="w-40 shrink-0 text-sm font-semibold text-ui-text-secondary">
    {label}
  </label>
  <input
    {id}
    type="text"
    class="flex-1 min-w-0 bg-ui-popup-bg text-ui-fg border border-ui-border rounded px-2 py-1 text-sm focus:border-ui-btn focus:outline-none"
    class:input-warning={invalid}
    {placeholder}
    bind:value
  />
</div>
