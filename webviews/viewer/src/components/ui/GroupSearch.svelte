<script lang="ts">
  import { groupSearchTerm } from '../../lib/state';
  import SearchIcon from '../../icons/SearchIcon.svelte';

  let { class: className = '' }: { class?: string } = $props();
  let inputEl: HTMLInputElement | undefined = $state();

  function clear() {
    groupSearchTerm.set('');
    inputEl?.focus();
  }
</script>

<div class="relative {className}">
  <span class="absolute left-2 top-1/2 -translate-y-1/2 text-ui-text-muted pointer-events-none">
    <SearchIcon class="size-3.5" />
  </span>
  <input
    bind:this={inputEl}
    bind:value={$groupSearchTerm}
    type="text"
    placeholder="Search groups…"
    spellcheck="false"
    autocomplete="off"
    class="w-full text-xs rounded-sm bg-ui-elem hover:bg-ui-elem-hover focus:bg-ui-elem-hover text-ui-fg pl-7 pr-6 py-1 outline-none placeholder:text-ui-text-muted"
  />
  {#if $groupSearchTerm}
    <button
      class="absolute right-1 top-1/2 -translate-y-1/2 size-4 flex items-center justify-center rounded-sm leading-none text-sm cursor-pointer text-ui-text-muted hover:text-ui-fg hover:bg-ui-elem-hover"
      onclick={clear}
      title="Clear search"
      aria-label="Clear search"
    >
      ×
    </button>
  {/if}
</div>
