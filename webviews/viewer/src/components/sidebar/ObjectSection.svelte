<script lang="ts">
  import { hiddenObjects, settings, sidebarHiddenGroups } from '../../lib/state';
  import type { GroupKind } from '../../lib/state';
  import { VisibilityManager } from '../../lib/commands/VisibilityManager';
  import GroupButton from './GroupButton.svelte';
  import ObjectIcon from '../../icons/ObjectIcon.svelte';
  import EyeIcon from '../../icons/EyeIcon.svelte';
  import EyeOffIcon from '../../icons/EyeOffIcon.svelte';

  let {
    objectKey,
    faces,
    nodes,
    volumes,
    edges,
    mixed,
    color,
  }: {
    objectKey: string;
    faces: string[];
    nodes: string[];
    volumes: string[];
    edges: string[];
    mixed: { name: string; kind: GroupKind }[];
    color: number[];
  } = $props();

  let groupByKind = $derived($settings.groupByKind);

  let objectName = $derived(objectKey.replace('all_', '').replace('.obj', ''));
  let colorCss = $derived(
    `rgb(${Math.round(color[0] * 255)},${Math.round(color[1] * 255)},${Math.round(color[2] * 255)})`
  );
  let isHidden = $derived($hiddenObjects.has(objectKey));
  let collapsed = $state(false);

  let hiddenGroupCount = $derived.by(() => {
    const hidden = $sidebarHiddenGroups.get(objectKey);
    if (!hidden) return 0;
    return [...volumes, ...faces, ...edges, ...nodes].filter((g) => hidden.has(g)).length;
  });

  let allGroupsHiddenFromSidebar = $derived.by(() => {
    const hidden = $sidebarHiddenGroups.get(objectKey);
    if (!hidden) return false;
    return [...volumes, ...faces, ...edges, ...nodes].every((g) => hidden.has(g));
  });

  let groupCount = $derived(volumes.length + faces.length + edges.length + nodes.length);

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
    oncontextmenu={(e) => {
      e.preventDefault();
      closeContextMenu();
    }}
    role="presentation"
  ></div>
  <div
    class="fixed z-[9999] bg-ui-popup-bg border border-ui-border rounded shadow-[0_4px_16px_rgba(0,0,0,0.25)] py-[3px] overflow-hidden"
    style="left: {contextMenu.x}px; top: {contextMenu.y}px"
  >
    <button
      class="flex items-center w-full px-[10px] py-[5px] text-xs cursor-pointer text-ui-fg whitespace-nowrap bg-transparent border-0 text-left hover:bg-ui-elem-hover"
      onclick={hideAllOthers}
    >
      Hide all other objects
    </button>
  </div>
{/if}

<span
  role="group"
  class="h-4.5 w-full self-stretch flex items-center gap-1 pl-1.25 pr-0.5 mb-2 not-nth-of-type-[1]:mt-1 text-xs font-bold text-ui-text-primary"
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
  <div class="w-full text-center text-[0.7rem] font-normal mb-2 text-ui-text-muted">
    {groupCount} groups
  </div>
{:else if !collapsed}
  <div class="w-full flex flex-col items-center space-y-1">
    {#if groupByKind}
      {#each volumes as groupName}
        <GroupButton {objectKey} {groupName} kind="volume" />
      {/each}
      {#each faces as groupName}
        <GroupButton {objectKey} {groupName} kind="face" />
      {/each}
      {#each edges as groupName}
        <GroupButton {objectKey} {groupName} kind="edge" />
      {/each}
      {#each nodes as groupName}
        <GroupButton {objectKey} {groupName} kind="node" />
      {/each}
    {:else}
      {#each mixed as { name, kind } (`${name}::${kind}`)}
        <GroupButton {objectKey} groupName={name} {kind} />
      {/each}
    {/if}
    {#if hiddenGroupCount > 0}
      <div class="w-full text-center text-[0.7rem] pb-1 text-ui-text-muted">
        {hiddenGroupCount} hidden
      </div>
    {/if}
  </div>
{:else}
  <div class="w-full text-center text-[0.7rem] font-normal mb-2 text-ui-text-muted">
    {groupCount} groups
  </div>
{/if}
