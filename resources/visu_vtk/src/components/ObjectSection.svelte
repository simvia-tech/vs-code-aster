<script lang="ts">
  import { hiddenObjects, sidebarHiddenGroups } from '../lib/state';
  import { VisibilityManager } from '../lib/commands/VisibilityManager';
  import GroupButton from './GroupButton.svelte';
  import ObjectIcon from '../icons/ObjectIcon.svelte';
  import EyeIcon from '../icons/EyeIcon.svelte';
  import EyeOffIcon from '../icons/EyeOffIcon.svelte';

  let {
    objectKey,
    faces,
    nodes,
    color,
  }: {
    objectKey: string;
    faces: string[];
    nodes: string[];
    color: number[];
  } = $props();

  let objectName = $derived(objectKey.replace('all_', '').replace('.obj', ''));
  let colorCss = $derived(`rgb(${Math.round(color[0] * 255)},${Math.round(color[1] * 255)},${Math.round(color[2] * 255)})`);
  let isHidden = $derived($hiddenObjects.has(objectKey));
  let collapsed = $state(false);

  let hiddenGroupCount = $derived.by(() => {
    const hidden = $sidebarHiddenGroups.get(objectKey);
    if (!hidden) return 0;
    return [...faces, ...nodes].filter((g) => hidden.has(g)).length;
  });

  let allGroupsHiddenFromSidebar = $derived.by(() => {
    const hidden = $sidebarHiddenGroups.get(objectKey);
    if (!hidden) return false;
    return [...faces, ...nodes].every((g) => hidden.has(g));
  });

  let groupCount = $derived(faces.length + nodes.length);

  function toggleVisibility() {
    VisibilityManager.Instance.toggleObjectVisibility(objectKey);
  }

  function toggleCollapsed() {
    if (isHidden || allGroupsHiddenFromSidebar) return;
    collapsed = !collapsed;
  }

  let contextMenu: { x: number; y: number } | null = $state(null);

  function onContextMenu(e: MouseEvent) {
    e.preventDefault();
    contextMenu = { x: e.clientX, y: e.clientY };
  }

  function closeContextMenu() {
    contextMenu = null;
  }

  function hideAllOthers() {
    VisibilityManager.Instance.hideAllOthers(objectKey);
    closeContextMenu();
  }
</script>

{#if contextMenu}
  <div
    class="fixed inset-0 z-40"
    onclick={closeContextMenu}
    oncontextmenu={(e) => { e.preventDefault(); closeContextMenu(); }}
    role="presentation"
  ></div>
  <div
    style="position: fixed; z-index: 9999; left: {contextMenu.x}px; top: {contextMenu.y}px; background: var(--ui-popup-bg); border: 1px solid var(--ui-border); border-radius: 4px; box-shadow: 0 4px 16px rgba(0,0,0,0.25); padding: 3px 0; overflow: hidden;"
  >
    <button
      style="display: flex; align-items: center; width: 100%; padding: 5px 10px; font-size: 0.75rem; cursor: pointer; color: var(--ui-fg); white-space: nowrap; background: none; border: none; text-align: left;"
      onmouseenter={(e) => (e.currentTarget as HTMLElement).style.background = 'var(--ui-element-bg-hover)'}
      onmouseleave={(e) => (e.currentTarget as HTMLElement).style.background = ''}
      onclick={hideAllOthers}
    >
      Hide all others
    </button>
  </div>
{/if}

<span
  class="h-4.5 w-full self-stretch flex items-center gap-1 pl-1.25 pr-0.5 mb-2 not-nth-of-type-[1]:mt-1 text-xs font-bold"
  style="color: var(--ui-text-primary)"
  oncontextmenu={onContextMenu}
>
  <span style="color: {colorCss}"><ObjectIcon class="size-[18px]" /></span>
  <span
    class="flex-1 truncate text-center px-2 select-none"
    style="cursor: {isHidden || allGroupsHiddenFromSidebar ? 'default' : 'pointer'}"
    onclick={toggleCollapsed}
    onkeydown={(e) => e.key === 'Enter' && toggleCollapsed()}
    role="button"
    tabindex="0"
  >
    {objectName}
  </span>
  <button
    class="size-4.5 shrink-0 flex items-center justify-center cursor-pointer opacity-40 hover:opacity-90"
    title="Hide/show mesh"
    onclick={toggleVisibility}
  >
    {#if isHidden}
      <EyeOffIcon class="size-4" />
    {:else}
      <EyeIcon class="size-4" />
    {/if}
  </button>
</span>

{#if isHidden}
  <div class="w-full text-center text-[0.7rem] font-normal mb-2" style="color: var(--ui-text-muted)">
    {groupCount} groups
  </div>
{:else}
  {#if !collapsed}
    <div class="w-full flex flex-col items-center space-y-1">
      {#each faces as groupName}
        <GroupButton {objectKey} {groupName} isFace={true} />
      {/each}
      {#each nodes as groupName}
        <GroupButton {objectKey} {groupName} isFace={false} />
      {/each}
      {#if hiddenGroupCount > 0}
        <div class="w-full text-center text-[0.7rem] pb-1" style="color: var(--ui-text-muted)">
          {hiddenGroupCount} hidden
        </div>
      {/if}
    </div>
  {:else}
    <div class="w-full text-center text-[0.7rem] font-normal mb-2" style="color: var(--ui-text-muted)">
      {groupCount} groups
    </div>
  {/if}
{/if}
