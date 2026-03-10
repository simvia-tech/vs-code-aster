<script lang="ts">
  import { groupHierarchy } from '../lib/state';
  import ObjectSection from './ObjectSection.svelte';
  import ActionButtons from './ActionButtons.svelte';
  import AxisButtons from './AxisButtons.svelte';

  let { onOpenGroups }: { onOpenGroups: () => void } = $props();
</script>

<div
  id="controls"
  class="relative h-full flex flex-col z-10 p-2"
  style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent)"
>
  <div
    class="flex flex-col items-center space-y-1 grow overflow-y-auto"
  >
    {#each Object.entries($groupHierarchy) as [key, data]}
      <ObjectSection
        objectKey={key}
        faces={data.faces}
        nodes={data.nodes}
        color={(data as any).color ?? [0.537, 0.529, 0.529]}
      />
    {/each}
  </div>

  <ActionButtons {onOpenGroups} />

  <div class="w-3/4 h-px my-2 mx-auto" style="background: var(--ui-border)"></div>

  <AxisButtons />
</div>
