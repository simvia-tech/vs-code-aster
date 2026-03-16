<script lang="ts">
  import type { Snippet } from 'svelte';

  export interface DropdownOption {
    value: string;
    label: string;
  }

  interface Props {
    options: DropdownOption[];
    value?: string | null;
    onSelect: (value: string) => void;
    align?: 'left' | 'right';
    children: Snippet;
  }

  let { options, value = null, onSelect, align = 'left', children }: Props = $props();

  let open = $state(false);
  let triggerEl = $state<HTMLElement | null>(null);
  let panelEl = $state<HTMLElement | null>(null);

  $effect(() => {
    if (!open || !panelEl || !triggerEl) return;
    const measureEl = (triggerEl.firstElementChild as HTMLElement) ?? triggerEl;
    const rect = measureEl.getBoundingClientRect();
    const panelW = Math.max(panelEl.offsetWidth, rect.width);
    const panelH = panelEl.offsetHeight;
    let left = rect.left + rect.width / 2 - panelW / 2;
    left = Math.max(4, Math.min(left, window.innerWidth - panelW - 4));
    const openUp = window.innerHeight - rect.bottom < panelH + 8;
    const top = openUp ? rect.top - panelH - 4 : rect.bottom + 4;
    panelEl.style.left = `${left}px`;
    panelEl.style.top = `${top}px`;
    panelEl.style.minWidth = `${panelW}px`;
  });

  function toggle(e: MouseEvent) {
    e.stopPropagation();
    open = !open;
  }

  function select(val: string) {
    onSelect(val);
    open = false;
  }

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

<div bind:this={triggerEl} style="display: contents" onclick={toggle} role="none">
  {@render children()}
</div>

{#if open}
  <div
    use:portal
    bind:this={panelEl}
    class="fixed z-[9999] bg-ui-popup-bg border border-ui-border rounded py-[3px] overflow-hidden shadow-[0_4px_16px_rgba(0,0,0,0.25)]"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
    role="menu"
    tabindex="-1"
  >
    {#each options as { value: val, label }}
      {@const isSelected = val === value}
      <div
        class="flex items-center gap-2 px-2.5 py-[5px] text-xs cursor-pointer text-ui-fg whitespace-nowrap hover:bg-ui-elem-hover {isSelected
          ? 'font-semibold'
          : ''} {align === 'right' ? 'justify-end' : ''}"
        role="menuitem"
        tabindex="0"
        onclick={() => select(val)}
        onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && select(val)}
      >
        {#if value !== null}
          <span class="text-[0.6rem] shrink-0 w-2.5 {isSelected ? '' : 'opacity-0'}">✓</span>
        {/if}
        <span>{label}</span>
      </div>
    {/each}
  </div>
{/if}
