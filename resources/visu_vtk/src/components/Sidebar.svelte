<script lang="ts">
  import { onMount } from 'svelte';
  import { groupHierarchy } from '../lib/state';
  import { VtkApp } from '../lib/core/VtkApp';
  import ObjectSection from './ObjectSection.svelte';
  import ActionButtons from './ActionButtons.svelte';
  import AxisButtons from './AxisButtons.svelte';

  let { onOpenGroups }: { onOpenGroups: () => void } = $props();

  onMount(() => {
    VtkApp.Instance.updateCameraOffset();
  });
</script>

<div
  id="controls"
  class="relative h-full flex flex-col z-10 p-2 bg-ui-muted"
>
  <div id="sidebarGroups" class="flex flex-col items-center space-y-1 grow overflow-y-auto">
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

  <div class="w-3/4 h-px my-2 mx-auto bg-ui-border"></div>

  <AxisButtons />
</div>
