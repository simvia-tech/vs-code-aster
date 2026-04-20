<script lang="ts">
  import { isInteger } from '../lib/types';

  interface Props {
    id: string;
    label: string;
    value: string;
    kind?: 'text' | 'int';
    placeholder?: string;
    error?: string;
    accent?: boolean;
    suffix?: string;
  }

  let {
    id,
    label,
    value = $bindable(),
    kind = 'text',
    placeholder = '',
    error = '',
    accent = false,
    suffix = '',
  }: Props = $props();

  let invalid = $derived(!!error || (kind === 'int' && !isInteger(value)));

  function handleKeydown(e: KeyboardEvent) {
    if (kind !== 'int') {
      return;
    }
    if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') {
      return;
    }
    if (!isInteger(value)) {
      return;
    }
    e.preventDefault();
    const n = Number(value) + (e.key === 'ArrowUp' ? 1 : -1);
    value = String(Math.max(0, n));
  }
</script>

<div class="flex flex-col gap-1">
  <div class="flex items-center gap-3">
    <label
      for={id}
      class="w-40 shrink-0 text-sm font-semibold cursor-pointer select-none {accent
        ? 'text-ui-fg'
        : 'text-ui-text-secondary'}"
    >
      {label}
    </label>
    <div class="flex-1 min-w-0 relative">
      <input
        {id}
        type="text"
        class="w-full bg-ui-input-bg text-ui-input-fg border border-ui-input-border rounded-sm py-1 text-sm focus:border-ui-focus focus:outline-none"
        class:input-warning={invalid}
        style={suffix
          ? `padding-left: 0.5rem; padding-right: calc(${suffix.length}ch + 0.75rem)`
          : 'padding-left: 0.5rem; padding-right: 0.5rem'}
        {placeholder}
        bind:value
        onkeydown={handleKeydown}
      />
      {#if suffix}
        <span
          class="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-ui-text-muted select-none pointer-events-none"
          aria-hidden="true"
        >
          {suffix}
        </span>
      {/if}
    </div>
  </div>
  {#if error}
    <p class="pl-40 ml-3 text-xs" style="color: var(--vscode-inputValidation-errorBorder, #d45858)">
      {error}
    </p>
  {/if}
</div>
