<script lang="ts">
  import { highlightedGroups, sidebarHiddenGroups } from '../../lib/state';
  import { VisibilityManager } from '../../lib/commands/VisibilityManager';
  import FaceIcon from '../../icons/FaceIcon.svelte';
  import NodeIcon from '../../icons/NodeIcon.svelte';
  import VolumeIcon from '../../icons/VolumeIcon.svelte';
  import EdgeIcon from '../../icons/EdgeIcon.svelte';
  import type { GroupKind } from '../../lib/data/Group';

  let {
    objectKey,
    groupName,
    kind,
  }: {
    objectKey: string;
    groupName: string;
    kind: GroupKind;
  } = $props();

  let fullKey = $derived(`${objectKey}::${groupName}::${kind}`);
  let highlight = $derived($highlightedGroups.get(fullKey));
  let isHidden = $derived($sidebarHiddenGroups.get(objectKey)?.has(groupName) ?? false);

  let bgStyle = $derived(
    highlight ? `rgb(${highlight[0] * 255}, ${highlight[1] * 255}, ${highlight[2] * 255}, 0.8)` : ''
  );
  let colorStyle = $derived(highlight ? 'var(--ui-highlight-text)' : 'var(--ui-text-primary)');

  function handleClick() {
    VisibilityManager.Instance.setVisibility(fullKey);
  }
</script>

{#if !isHidden}
  <button
    class="relative flex items-center justify-center rounded-sm text-xs px-2 pt-0.75 pb-1.25 w-full cursor-pointer {!highlight
      ? 'bg-ui-elem hover:bg-ui-elem-hover'
      : ''}"
    style="{highlight ? `background: ${bgStyle};` : ''} color: {colorStyle}; {highlight
      ? 'font-weight: 600;'
      : ''}"
    onclick={handleClick}
  >
    <span class="absolute left-1.5 top-1">
      {#if kind === 'face'}
        <FaceIcon class="size-4" />
      {:else if kind === 'volume'}
        <VolumeIcon class="size-4" />
      {:else if kind === 'edge'}
        <EdgeIcon class="size-4" />
      {:else}
        <NodeIcon class="size-4" />
      {/if}
    </span>
    <span class="pl-5">{groupName}</span>
  </button>
{/if}
