<script lang="ts">
  import Checkbox from './Checkbox.svelte';

  export interface MultiSelectOption {
    value: string;
    label: string;
    hint?: string;
  }

  let {
    options,
    selected,
    onToggle,
    placeholder = 'Select…',
  }: {
    options: MultiSelectOption[];
    selected: string[];
    onToggle: (value: string) => void;
    placeholder?: string;
  } = $props();

  let open = $state(false);
  let triggerEl = $state<HTMLElement | null>(null);
  let panelEl = $state<HTMLElement | null>(null);

  const summary = $derived(
    selected.length === 0
      ? placeholder
      : options
          .filter((o) => selected.includes(o.value))
          .map((o) => o.label)
          .join(', ')
  );

  $effect(() => {
    if (!open || !panelEl || !triggerEl) {
      return;
    }
    const rect = triggerEl.getBoundingClientRect();
    const panelW = Math.max(panelEl.offsetWidth, rect.width);
    const panelH = panelEl.offsetHeight;
    let left = Math.max(4, Math.min(rect.left, window.innerWidth - panelW - 4));
    const openUp = window.innerHeight - rect.bottom < panelH + 8;
    const top = openUp ? rect.top - panelH - 4 : rect.bottom + 4;
    panelEl.style.left = `${left}px`;
    panelEl.style.top = `${top}px`;
    panelEl.style.minWidth = `${panelW}px`;
  });

  function portal(node: HTMLElement) {
    document.body.appendChild(node);
    return {
      destroy() {
        node.remove();
      },
    };
  }
</script>

<svelte:document onclick={() => (open = false)} />

<button
  type="button"
  bind:this={triggerEl}
  onclick={(e) => {
    e.stopPropagation();
    open = !open;
  }}
  class="flex w-full cursor-pointer items-center justify-between gap-1 rounded border border-ui-input-border bg-ui-input-bg px-2 py-1 text-ui-input-fg"
>
  <span class="truncate {selected.length === 0 ? 'text-ui-text-muted' : ''}">{summary}</span>
  <svg width="8" height="8" viewBox="0 0 8 8" fill="currentColor" aria-hidden="true">
    <path d="M1 2.5 L4 5.5 L7 2.5 Z" />
  </svg>
</button>

{#if open}
  <div
    use:portal
    bind:this={panelEl}
    class="no-scrollbar fixed z-[9999] max-h-[60vh] overflow-y-auto rounded border border-ui-border bg-ui-popup-bg py-[3px] shadow-[0_4px_16px_rgba(0,0,0,0.25)]"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
    role="menu"
    tabindex="-1"
  >
    {#if options.length === 0}
      <div class="px-2.5 py-1 text-xs text-ui-text-muted">No groups</div>
    {/if}
    {#each options as o (o.value)}
      <Checkbox
        block
        checked={selected.includes(o.value)}
        label={o.label}
        hint={o.hint}
        onchange={() => onToggle(o.value)}
      />
    {/each}
  </div>
{/if}
