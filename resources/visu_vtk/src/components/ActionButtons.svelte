<script lang="ts">
  import { VisibilityManager } from '../lib/commands/VisibilityManager';
  import FilterIcon from '../icons/FilterIcon.svelte';
  import ClearIcon from '../icons/ClearIcon.svelte';

  let { onOpenGroups }: { onOpenGroups: () => void } = $props();

  function clear() {
    VisibilityManager.Instance.clear();
  }
</script>

<div
  id="sidebarActions"
  class="absolute left-full top-1 flex flex-col items-center rounded-r-sm border-l"
  style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border-color: var(--ui-border)"
>
  <div class="group flex items-center">
    <button
      class="size-6 p-1 flex items-center justify-center cursor-pointer hover:bg-ui-elem"
      onclick={onOpenGroups}
    >
      <FilterIcon class="size-3.5" />
    </button>
    <span
      class="absolute left-full pl-1.5 hidden group-hover:inline whitespace-nowrap"
      style="color: var(--ui-text-secondary)"
    >
      Select groups to show in sidebar
    </span>
  </div>
  <div class="w-3/4 h-px mx-auto" style="background: var(--ui-border)"></div>
  <div class="group flex items-center">
    <button
      class="size-6 p-1 flex items-center justify-center cursor-pointer hover:bg-ui-elem"
      onclick={clear}
    >
      <ClearIcon class="size-3.5" />
    </button>
    <span
      class="absolute left-full pl-1.5 hidden group-hover:inline whitespace-nowrap"
      style="color: var(--ui-text-secondary)"
    >
      Clear highlighted groups
    </span>
  </div>
</div>
