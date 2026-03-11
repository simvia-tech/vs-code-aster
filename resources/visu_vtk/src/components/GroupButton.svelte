<script lang="ts">
  import { highlightedGroups, sidebarHiddenGroups } from '../lib/state';
  import { VisibilityManager } from '../lib/commands/VisibilityManager';
  import FaceIcon from '../icons/FaceIcon.svelte';
  import NodeIcon from '../icons/NodeIcon.svelte';

  let {
    objectKey,
    groupName,
    isFace,
  }: {
    objectKey: string;
    groupName: string;
    isFace: boolean;
  } = $props();

  let highlight = $derived($highlightedGroups.get(`${objectKey}::${groupName}`));
  let isHidden = $derived($sidebarHiddenGroups.get(objectKey)?.has(groupName) ?? false);

  let bgStyle = $derived(
    highlight ? `rgb(${highlight[0] * 255}, ${highlight[1] * 255}, ${highlight[2] * 255}, 0.8)` : '',
  );
  let colorStyle = $derived(highlight ? 'var(--ui-highlight-text)' : 'var(--ui-text-primary)');

  function handleClick() {
    VisibilityManager.Instance.setVisibility(`${objectKey}::${groupName}`);
  }
</script>

{#if !isHidden}
  <button
    class="relative flex items-center justify-center rounded-sm text-xs px-2 pt-0.75 pb-1.25 w-full cursor-pointer {!highlight ? 'bg-ui-elem hover:bg-ui-elem-hover' : ''}"
    style="{highlight ? `background: ${bgStyle};` : ''} color: {colorStyle}; {highlight ? 'font-weight: 600;' : ''}"
    onclick={handleClick}
  >
    <span class="absolute left-1.5 top-1">
      {#if isFace}
        <FaceIcon class="size-4" />
      {:else}
        <NodeIcon class="size-4" />
      {/if}
    </span>
    <span class="pl-5">{groupName}</span>
  </button>
{/if}
