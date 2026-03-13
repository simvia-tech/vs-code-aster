<script lang="ts">
  import { groupHierarchy, sidebarHiddenGroups } from '../../lib/state';
  import FaceIcon from '../../icons/FaceIcon.svelte';
  import NodeIcon from '../../icons/NodeIcon.svelte';
  import ObjectIcon from '../../icons/ObjectIcon.svelte';

  let { onclose }: { onclose: () => void } = $props();

  let objects = $derived(
    Object.entries($groupHierarchy).map(([key, data]) => {
      const [r, g, b] = (data as any).color ?? [0.537, 0.529, 0.529];
      const faces = data.faces;
      const nodes = data.nodes;
      return {
        key,
        name: key.replace('all_', '').replace('.obj', ''),
        color: [r, g, b],
        allGroups: [
          ...faces.map((name) => ({ name, isFace: true })),
          ...nodes.map((name) => ({ name, isFace: false })),
        ],
      };
    })
  );

  function isVisible(objectKey: string, groupName: string): boolean {
    return !($sidebarHiddenGroups.get(objectKey)?.has(groupName) ?? false);
  }

  function toggleGroup(objectKey: string, groupName: string) {
    sidebarHiddenGroups.update((map) => {
      const newMap = new Map(map);
      const set = new Set(newMap.get(objectKey) ?? []);
      if (set.has(groupName)) set.delete(groupName);
      else set.add(groupName);
      newMap.set(objectKey, set);
      return newMap;
    });
  }

  function allUnchecked(objectKey: string, allGroups: { name: string }[]): boolean {
    const hidden = $sidebarHiddenGroups.get(objectKey);
    if (!hidden) return false;
    return allGroups.every((g) => hidden.has(g.name));
  }

  function toggleAll(objectKey: string, allGroups: { name: string }[]) {
    const allOff = allUnchecked(objectKey, allGroups);
    sidebarHiddenGroups.update((map) => {
      const newMap = new Map(map);
      if (allOff) {
        newMap.delete(objectKey);
      } else {
        newMap.set(objectKey, new Set(allGroups.map((g) => g.name)));
      }
      return newMap;
    });
  }

  function resetAll() {
    sidebarHiddenGroups.set(new Map());
  }

  function colorCss(color: number[]): string {
    const [r, g, b] = color;
    return `rgb(${Math.round(r * 255)},${Math.round(g * 255)},${Math.round(b * 255)})`;
  }
</script>

<div
  id="groupsPopup"
  class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-2/3 max-h-2/3 rounded shadow-lg backdrop-blur-lg p-8 flex flex-col bg-ui-popup-bg text-ui-fg border border-ui-border"
  role="document"
>
  <div class="flex flex-col mb-4">
    <span class="font-bold text-base">Sidebar groups</span>
    <span class="text-xs mt-1 text-ui-text-secondary">
      Choose which groups are shown in the sidebar. Hidden groups remain visible in the 3D view.
    </span>
  </div>

  <div class="columns-2 gap-6 overflow-y-auto grow">
    {#each objects as obj (obj.key)}
      {@const allOff = allUnchecked(obj.key, obj.allGroups)}
      <div class="break-inside-avoid flex flex-col space-y-1.5 mb-5">
        <div class="flex items-center justify-between pb-1 border-b border-ui-border">
          <div class="flex items-center gap-1.5">
            <span style="color: {colorCss(obj.color)}"><ObjectIcon class="size-4 shrink-0" /></span>
            <span class="font-semibold text-sm">{obj.name}</span>
          </div>
          <button
            class="text-xs leading-none cursor-pointer px-1.5 py-0.5 rounded-sm hover:bg-ui-elem text-ui-text-secondary"
            onclick={() => toggleAll(obj.key, obj.allGroups)}
          >
            {allOff ? 'Show all' : 'Hide all'}
          </button>
        </div>

        {#each obj.allGroups as group}
          <label class="flex items-center gap-1.5 cursor-pointer select-none">
            <input
              type="checkbox"
              class="custom-cb"
              checked={isVisible(obj.key, group.name)}
              onchange={() => toggleGroup(obj.key, group.name)}
            />
            {#if group.isFace}
              <FaceIcon class="size-3.5 shrink-0" />
            {:else}
              <NodeIcon class="size-3.5 shrink-0" />
            {/if}
            <span class="text-xs truncate -translate-y-px">{group.name}</span>
          </label>
        {/each}
      </div>
    {/each}
  </div>

  <div class="mt-4 flex justify-between items-center">
    <button
      class="px-3 py-1 rounded-sm cursor-pointer text-xs bg-ui-elem hover:bg-ui-elem-hover text-ui-fg border border-ui-border"
      onclick={resetAll}
    >
      Reset
    </button>
    <button
      class="font-bold px-3 py-1 rounded-sm cursor-pointer text-xs bg-ui-btn hover:bg-ui-btn-hover text-ui-btn-fg"
      onclick={onclose}
    >
      Close
    </button>
  </div>
</div>
