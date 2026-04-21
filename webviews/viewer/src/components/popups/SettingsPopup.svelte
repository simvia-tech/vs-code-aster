<script lang="ts">
  import { settings } from '../../lib/state';
  import { GlobalSettings } from '../../lib/settings/GlobalSettings';
  import { CameraManager } from '../../lib/interaction/CameraManager';
  import { VtkApp } from '../../lib/core/VtkApp';
  import { VisibilityManager } from '../../lib/commands/VisibilityManager';
  import { Controller } from '../../lib/Controller';
  import ChevronIcon from '../../icons/ChevronIcon.svelte';
  import Toggle from '../ui/Toggle.svelte';
  import Dropdown from '../ui/Dropdown.svelte';
  import type { EdgeMode, SidebarSort } from '../../lib/state';

  let { onclose }: { onclose: () => void } = $props();

  const tabs = ['Mesh edges', 'Groups', 'Visibility', 'Display'] as const;
  type Tab = (typeof tabs)[number];
  let activeTab = $state<Tab>('Mesh edges');

  const edgeModeOptions = [
    { value: 'threshold', label: 'Show mesh edges when zooming (threshold)' },
    { value: 'gradual', label: 'Show mesh edges when zooming (gradual)' },
    { value: 'show', label: 'Always show mesh edges' },
    { value: 'hide', label: 'Always hide mesh edges' },
  ];

  const edgeModeDescriptions: Record<EdgeMode, string> = {
    gradual:
      'Mesh edges fade in as you zoom in, scaled by mesh density. When zoomed out, large meshes may appear very flat as outer edges are mostly hidden. Performance is impacted.',
    threshold:
      'Mesh edges appear abruptly at a zoom level based on mesh density. When zoomed out, large meshes may appear slightly flat as outer edges are hidden. Performance is not impacted.',
    show: 'Mesh edges are always visible. Large meshes will appear almost entirely black when zoomed out. Performance is impacted.',
    hide: 'Mesh edges are always hidden. All shapes will look slightly flat regardless of zoom level or mesh size.',
  };

  const sidebarSortOptions = [
    { value: 'natural', label: 'Alphabetical (natural)' },
    { value: 'size', label: 'By size (largest first)' },
  ];

  let hiddenOpacityPct = $derived(Math.round($settings.hiddenObjectOpacity * 100));
  let edgeThresholdDisplay = $derived(parseFloat($settings.edgeThresholdMultiplier.toFixed(2)));
  let edgeGroupThicknessDisplay = $derived($settings.edgeGroupThickness);
  let nodeGroupSizeDisplay = $derived(parseFloat($settings.nodeGroupSize.toFixed(2)));
  let sidebarSortLabel = $derived(
    sidebarSortOptions.find((o) => o.value === $settings.sidebarSort)?.label ??
      $settings.sidebarSort
  );
  let edgeModeLabel = $derived(
    edgeModeOptions.find((o) => o.value === $settings.edgeMode)?.label ?? $settings.edgeMode
  );
  let edgeModeDesc = $derived(edgeModeDescriptions[$settings.edgeMode] ?? '');
  let showThresholdSection = $derived($settings.edgeMode === 'threshold');
  let groupTransparencyPct = $derived(Math.round($settings.groupTransparency * 100));

  function applyEdgeMode(mode: EdgeMode) {
    GlobalSettings.Instance.edgeMode = mode;
    settings.update((s) => ({ ...s, edgeMode: mode }));
    if (CameraManager.Instance.faceGroups) {
      CameraManager.Instance.refreshEdgeVisibility();
    }
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { edgeMode: mode },
    });
  }

  function onHiddenOpacityInput(e: Event) {
    const raw = parseInt((e.target as HTMLInputElement).value, 10);
    const pct = Math.min(raw, 50);
    (e.target as HTMLInputElement).value = String(pct);
    const opacity = pct / 100;
    GlobalSettings.Instance.hiddenObjectOpacity = opacity;
    settings.update((s) => ({ ...s, hiddenObjectOpacity: opacity }));
    VisibilityManager.Instance.applyHiddenObjectOpacity();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { hiddenObjectOpacity: opacity },
    });
  }

  function onEdgeThresholdInput(e: Event) {
    const multiplier = parseInt((e.target as HTMLInputElement).value, 10) / 100;
    GlobalSettings.Instance.edgeThresholdMultiplier = multiplier;
    settings.update((s) => ({ ...s, edgeThresholdMultiplier: multiplier }));
    if (CameraManager.Instance.faceGroups) {
      CameraManager.Instance.refreshEdgeVisibility();
    }
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { edgeThresholdMultiplier: multiplier },
    });
  }

  function onEdgeGroupThicknessInput(e: Event) {
    const thickness = parseInt((e.target as HTMLInputElement).value, 10);
    GlobalSettings.Instance.edgeGroupThickness = thickness;
    settings.update((s) => ({ ...s, edgeGroupThickness: thickness }));
    VisibilityManager.Instance.applyEdgeGroupThickness();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { edgeGroupThickness: thickness },
    });
  }

  function toggleEdgeGroupDepthOffset() {
    const enabled = !$settings.edgeGroupDepthOffset;
    GlobalSettings.Instance.edgeGroupDepthOffset = enabled;
    settings.update((s) => ({ ...s, edgeGroupDepthOffset: enabled }));
    VisibilityManager.Instance.applyEdgeGroupDepthOffset();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { edgeGroupDepthOffset: enabled },
    });
  }

  function onNodeGroupSizeInput(e: Event) {
    const value = parseInt((e.target as HTMLInputElement).value, 10) / 100;
    GlobalSettings.Instance.nodeGroupSize = value;
    settings.update((s) => ({ ...s, nodeGroupSize: value }));
    CameraManager.Instance.refreshNodeGroupSize();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { nodeGroupSize: value },
    });
  }

  function applySidebarSort(sort: SidebarSort) {
    GlobalSettings.Instance.sidebarSort = sort;
    settings.update((s) => ({ ...s, sidebarSort: sort }));
    Controller.Instance.applySortOrder();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { sidebarSort: sort },
    });
  }

  function toggleGroupByKind() {
    const enabled = !$settings.groupByKind;
    GlobalSettings.Instance.groupByKind = enabled;
    settings.update((s) => ({ ...s, groupByKind: enabled }));
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { groupByKind: enabled },
    });
  }

  function onGroupTransparencyInput(e: Event) {
    const raw = parseInt((e.target as HTMLInputElement).value, 10);
    const pct = Math.min(raw, 50);
    (e.target as HTMLInputElement).value = String(pct);
    const opacity = pct / 100;
    GlobalSettings.Instance.groupTransparency = opacity;
    settings.update((s) => ({ ...s, groupTransparency: opacity }));
    VisibilityManager.Instance.applyGroupTransparency();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { groupTransparency: opacity },
    });
  }

  function toggleDreamBackground() {
    const enabled = !$settings.dreamBackground;
    GlobalSettings.Instance.dreamBackground = enabled;
    settings.update((s) => ({ ...s, dreamBackground: enabled }));
    VtkApp.Instance.setTransparentBackground(enabled);
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { dreamBackground: enabled },
    });
  }

  function toggleOrientationWidget() {
    const showOrientationWidget = !$settings.showOrientationWidget;
    GlobalSettings.Instance.showOrientationWidget = showOrientationWidget;
    settings.update((s) => ({ ...s, showOrientationWidget }));
    CameraManager.Instance.setOrientationWidgetVisible(showOrientationWidget);
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { showOrientationWidget },
    });
  }

  const EDGE_DEFAULTS = {
    edgeMode: 'threshold' as EdgeMode,
    edgeThresholdMultiplier: 1,
  };
  const GROUPS_DEFAULTS = {
    edgeGroupThickness: 3,
    edgeGroupDepthOffset: true,
    nodeGroupSize: 1,
    sidebarSort: 'natural' as SidebarSort,
    groupByKind: true,
  };
  const VISIBILITY_DEFAULTS = {
    hiddenObjectOpacity: 0,
    groupTransparency: 0.2,
  };
  const DISPLAY_DEFAULTS = { showOrientationWidget: true, dreamBackground: false };

  function resetMeshEdgesTab() {
    GlobalSettings.Instance.edgeMode = EDGE_DEFAULTS.edgeMode;
    GlobalSettings.Instance.edgeThresholdMultiplier = EDGE_DEFAULTS.edgeThresholdMultiplier;
    settings.update((s) => ({ ...s, ...EDGE_DEFAULTS }));
    CameraManager.Instance.refreshEdgeVisibility();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: EDGE_DEFAULTS,
    });
  }

  function resetGroupsTab() {
    GlobalSettings.Instance.edgeGroupThickness = GROUPS_DEFAULTS.edgeGroupThickness;
    GlobalSettings.Instance.edgeGroupDepthOffset = GROUPS_DEFAULTS.edgeGroupDepthOffset;
    GlobalSettings.Instance.nodeGroupSize = GROUPS_DEFAULTS.nodeGroupSize;
    GlobalSettings.Instance.sidebarSort = GROUPS_DEFAULTS.sidebarSort;
    GlobalSettings.Instance.groupByKind = GROUPS_DEFAULTS.groupByKind;
    settings.update((s) => ({ ...s, ...GROUPS_DEFAULTS }));
    VisibilityManager.Instance.applyEdgeGroupThickness();
    VisibilityManager.Instance.applyEdgeGroupDepthOffset();
    CameraManager.Instance.refreshNodeGroupSize();
    Controller.Instance.applySortOrder();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: GROUPS_DEFAULTS,
    });
  }

  function resetVisibilityTab() {
    GlobalSettings.Instance.hiddenObjectOpacity = VISIBILITY_DEFAULTS.hiddenObjectOpacity;
    GlobalSettings.Instance.groupTransparency = VISIBILITY_DEFAULTS.groupTransparency;
    settings.update((s) => ({ ...s, ...VISIBILITY_DEFAULTS }));
    VisibilityManager.Instance.applyHiddenObjectOpacity();
    VisibilityManager.Instance.applyGroupTransparency();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: VISIBILITY_DEFAULTS,
    });
  }

  function resetDisplayTab() {
    GlobalSettings.Instance.showOrientationWidget = DISPLAY_DEFAULTS.showOrientationWidget;
    GlobalSettings.Instance.dreamBackground = DISPLAY_DEFAULTS.dreamBackground;
    settings.update((s) => ({ ...s, ...DISPLAY_DEFAULTS }));
    CameraManager.Instance.setOrientationWidgetVisible(true);
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: DISPLAY_DEFAULTS,
    });
  }

  function resetSettings() {
    const defaults = {
      ...EDGE_DEFAULTS,
      ...GROUPS_DEFAULTS,
      ...VISIBILITY_DEFAULTS,
      ...DISPLAY_DEFAULTS,
    };
    GlobalSettings.Instance.hiddenObjectOpacity = defaults.hiddenObjectOpacity;
    GlobalSettings.Instance.edgeMode = defaults.edgeMode;
    GlobalSettings.Instance.edgeThresholdMultiplier = defaults.edgeThresholdMultiplier;
    GlobalSettings.Instance.edgeGroupThickness = defaults.edgeGroupThickness;
    GlobalSettings.Instance.edgeGroupDepthOffset = defaults.edgeGroupDepthOffset;
    GlobalSettings.Instance.nodeGroupSize = defaults.nodeGroupSize;
    GlobalSettings.Instance.sidebarSort = defaults.sidebarSort;
    GlobalSettings.Instance.groupByKind = defaults.groupByKind;
    GlobalSettings.Instance.groupTransparency = defaults.groupTransparency;
    GlobalSettings.Instance.showOrientationWidget = defaults.showOrientationWidget;
    GlobalSettings.Instance.dreamBackground = defaults.dreamBackground;
    settings.update((s) => ({ ...s, ...defaults }));
    VisibilityManager.Instance.applyHiddenObjectOpacity();
    VisibilityManager.Instance.applyGroupTransparency();
    VisibilityManager.Instance.applyEdgeGroupThickness();
    VisibilityManager.Instance.applyEdgeGroupDepthOffset();
    CameraManager.Instance.refreshEdgeVisibility();
    CameraManager.Instance.refreshNodeGroupSize();
    CameraManager.Instance.setOrientationWidgetVisible(true);
    Controller.Instance.applySortOrder();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: defaults,
    });
  }

  const tabResets: Record<Tab, () => void> = {
    'Mesh edges': resetMeshEdgesTab,
    Groups: resetGroupsTab,
    Visibility: resetVisibilityTab,
    Display: resetDisplayTab,
  };
</script>

{#snippet tip(text: string)}
  <span class="relative group cursor-help shrink-0 text-ui-text-muted">
    <span class="text-[0.65rem] leading-none select-none font-bold">ⓘ</span>
    <span
      class="pointer-events-none invisible group-hover:visible absolute top-full left-0 z-50 mt-1.5 w-56 rounded px-2 py-1.5 text-xs font-normal bg-ui-popup-bg border border-ui-border text-ui-fg shadow-[0_2px_8px_rgba(0,0,0,0.2)]"
    >
      {text}
    </span>
  </span>
{/snippet}

<div
  id="settingsPopup"
  class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[min(36rem,80vw)] h-[min(22rem,70vh)] rounded shadow-lg flex text-ui-fg border border-ui-border"
  role="document"
>
  <div class="absolute inset-0 rounded backdrop-blur-lg pointer-events-none bg-ui-popup-bg"></div>
  <nav class="relative z-10 flex flex-col py-4 shrink-0 w-36 border-r border-ui-border">
    <span class="font-bold text-sm px-4 pb-3 text-ui-text-primary">Settings</span>
    {#each tabs as tab}
      <button
        class="text-left text-xs px-4 py-2 cursor-pointer transition-colors hover:bg-ui-elem {activeTab ===
        tab
          ? 'bg-ui-elem text-ui-link font-semibold'
          : 'text-ui-text-secondary'}"
        onclick={() => (activeTab = tab)}
      >
        {tab}
      </button>
    {/each}
    <div class="grow"></div>
    <div class="px-4">
      <button
        class="w-full px-2 py-1 rounded-sm cursor-pointer text-xs bg-ui-elem hover:bg-ui-elem-hover text-ui-fg border border-ui-border"
        onclick={resetSettings}
      >
        Reset defaults
      </button>
    </div>
  </nav>

  <div class="relative z-10 flex flex-col flex-1 min-w-0 px-6 pt-6 pb-4">
    <div class="grow overflow-y-auto min-h-0 pr-1">
      {#if activeTab === 'Mesh edges'}
        <div class="flex flex-col space-y-2">
          <span class="text-xs text-ui-text-secondary pb-1">
            Controls the wireframe edges drawn on every cell of the mesh. For the display of edge
            <em>groups</em> (1D named entities from the .med file), see the <strong>Groups</strong>
            tab.
          </span>
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-medium">Mesh edge rendering mode</span>
            {@render tip(
              'Choose when the wireframe lines drawn on each cell of the mesh are visible. This does not affect edge groups (1D named entities from the .med file).'
            )}
          </div>
          <Dropdown
            options={edgeModeOptions}
            value={$settings.edgeMode}
            onSelect={(v) => applyEdgeMode(v as EdgeMode)}
          >
            <div
              class="w-full text-xs px-2 py-1.5 rounded-sm cursor-pointer flex items-center justify-between gap-2 select-none bg-ui-elem hover:bg-ui-elem-hover text-ui-fg border border-ui-border"
              role="button"
              tabindex="0"
            >
              <span class="truncate">{edgeModeLabel}</span>
              <ChevronIcon class="size-3 shrink-0" />
            </div>
          </Dropdown>
          <span class="text-xs text-ui-text-secondary">
            {edgeModeDesc}
          </span>
          {#if showThresholdSection}
            <div class="flex flex-col space-y-1.5 pt-1">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <label for="edgeThresholdRange" class="text-xs font-medium">
                    Threshold sensitivity
                  </label>
                  {@render tip(
                    'Higher values show edges at a lower zoom level, from farther away.'
                  )}
                </div>
                <span class="text-xs text-ui-text-secondary">
                  {edgeThresholdDisplay.toPrecision(edgeThresholdDisplay < 1 ? 2 : 3)}×
                </span>
              </div>
              <input
                id="edgeThresholdRange"
                type="range"
                min="25"
                max="500"
                step="5"
                value={Math.round($settings.edgeThresholdMultiplier * 100)}
                class="w-full cursor-pointer focus:outline-none accent-(--vscode-textLink-foreground,#0078d4)"
                oninput={onEdgeThresholdInput}
              />
              <span class="text-xs text-ui-text-secondary"
                >Higher values show edges from farther away.</span
              >
            </div>
          {/if}
        </div>
      {:else if activeTab === 'Groups'}
        <div class="flex flex-col space-y-3">
          <span class="text-xs text-ui-text-secondary pb-1">
            Per-kind display settings for the named groups (volumes, faces, edges, nodes) that come
            from the .med file.
          </span>

          <div class="flex flex-col space-y-1.5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <label for="edgeGroupThicknessRange" class="text-xs font-medium"
                  >Edge group thickness</label
                >
                {@render tip(
                  'Line width used to render edge groups (1D named entities from the .med file). Independent from the wireframe edges drawn on mesh cells.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary">{edgeGroupThicknessDisplay}px</span>
            </div>
            <input
              id="edgeGroupThicknessRange"
              type="range"
              min="1"
              max="10"
              step="1"
              value={$settings.edgeGroupThickness}
              class="w-full cursor-pointer focus:outline-none [accent-color:var(--vscode-textLink-foreground,#0078d4)]"
              oninput={onEdgeGroupThicknessInput}
            />
          </div>

          <div class="flex items-center gap-3">
            <Toggle
              checked={$settings.edgeGroupDepthOffset}
              onclick={toggleEdgeGroupDepthOffset}
              ariaLabel="Edge groups depth offset"
            />
            <div class="flex flex-col gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-medium">Edge groups above the mesh</span>
                {@render tip(
                  'Force edge groups to render on top of the mesh to avoid z-fighting (flicker). Disable if lines appear in the wrong position.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary"
                >Nudge edge groups toward the camera so they sit cleanly on top of the surface.</span
              >
            </div>
          </div>

          <div class="flex flex-col space-y-1.5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <label for="nodeGroupSizeRange" class="text-xs font-medium"
                  >Node group point size</label
                >
                {@render tip(
                  'Multiplier applied to the size of node-group points. Points still scale with zoom; this controls their base size.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary">{nodeGroupSizeDisplay}×</span>
            </div>
            <input
              id="nodeGroupSizeRange"
              type="range"
              min="25"
              max="400"
              step="5"
              value={Math.round($settings.nodeGroupSize * 100)}
              class="w-full cursor-pointer focus:outline-none [accent-color:var(--vscode-textLink-foreground,#0078d4)]"
              oninput={onNodeGroupSizeInput}
            />
          </div>

          <div class="flex items-center gap-3">
            <Toggle
              checked={$settings.groupByKind}
              onclick={toggleGroupByKind}
              ariaLabel="Group by kind"
            />
            <div class="flex flex-col gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-medium">Bucket groups by kind</span>
                {@render tip(
                  'When on, groups are displayed per kind in the sidebar (volumes, then faces, then edges, then nodes). When off, all groups of an object share a single list sorted by the Sidebar sort order.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary"
                >Separate volumes, faces, edges and nodes into distinct sections.</span
              >
            </div>
          </div>

          <div class="flex flex-col space-y-1.5">
            <div class="flex items-center gap-1.5">
              <span class="text-xs font-medium">Sidebar sort order</span>
              {@render tip(
                'Order used for groups in the sidebar. With buckets on, sorts within each kind; with buckets off, sorts across all groups of an object.'
              )}
            </div>
            <Dropdown
              options={sidebarSortOptions}
              value={$settings.sidebarSort}
              onSelect={(v) => applySidebarSort(v as SidebarSort)}
            >
              <div
                class="w-full text-xs px-2 py-1.5 rounded-sm cursor-pointer flex items-center justify-between gap-2 select-none bg-ui-elem hover:bg-ui-elem-hover text-ui-fg border border-ui-border"
                role="button"
                tabindex="0"
              >
                <span class="truncate">{sidebarSortLabel}</span>
                <ChevronIcon class="size-3 shrink-0" />
              </div>
            </Dropdown>
          </div>
        </div>
      {:else if activeTab === 'Visibility'}
        <div class="flex flex-col space-y-2">
          <div class="flex flex-col space-y-1.5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <label for="hiddenOpacityRange" class="text-xs font-medium"
                  >Hidden objects opacity</label
                >
                {@render tip(
                  'At 0% hidden objects are fully invisible. Above 0% they remain as faint ghosts.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary">{hiddenOpacityPct}%</span>
            </div>
            <input
              id="hiddenOpacityRange"
              type="range"
              min="0"
              max="100"
              step="1"
              value={hiddenOpacityPct}
              class="w-full cursor-pointer focus:outline-none [accent-color:var(--vscode-textLink-foreground,#0078d4)]"
              oninput={onHiddenOpacityInput}
            />
            <span class="text-xs text-ui-text-secondary"
              >When hiding an object with the eye button, it can remain slightly visible as a ghost.</span
            >
          </div>
          <div class="flex flex-col space-y-1.5 pt-1">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <label for="groupTransparencyRange" class="text-xs font-medium"
                  >Group selection transparency</label
                >
                {@render tip(
                  'When a sub-group is highlighted, the parent mesh fades to this opacity so the selected group stands out.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary">{groupTransparencyPct}%</span>
            </div>
            <input
              id="groupTransparencyRange"
              type="range"
              min="0"
              max="100"
              step="1"
              value={groupTransparencyPct}
              class="w-full cursor-pointer focus:outline-none [accent-color:var(--vscode-textLink-foreground,#0078d4)]"
              oninput={onGroupTransparencyInput}
            />
            <span class="text-xs text-ui-text-secondary"
              >Opacity of the parent mesh when a sub-group is highlighted.</span
            >
          </div>
        </div>
      {:else if activeTab === 'Display'}
        <div class="flex flex-col space-y-3">
          <div class="flex items-center gap-3">
            <Toggle
              checked={$settings.showOrientationWidget}
              onclick={toggleOrientationWidget}
              ariaLabel="Show orientation widget"
            />
            <div class="flex flex-col gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-medium">Orientation widget</span>
                {@render tip(
                  'Toggle the XYZ axes indicator in the bottom-right corner of the viewport.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary"
                >Show the axes widget in the bottom-right corner.</span
              >
            </div>
          </div>

          <div class="flex items-center gap-3">
            <Toggle
              checked={$settings.dreamBackground}
              onclick={toggleDreamBackground}
              ariaLabel="Dream background"
            />
            <div class="flex flex-col gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-medium">Dream background</span>
                {@render tip(
                  'Cosmetic only: animated EDF orange and blue light blobs slowly breathing behind the mesh. Does not affect lighting on the mesh itself.'
                )}
              </div>
              <span class="text-xs text-ui-text-secondary"
                >Animated colored glows behind the mesh, purely decorative.</span
              >
            </div>
          </div>
        </div>
      {/if}
    </div>

    <div class="pt-4 flex items-center justify-between">
      <button
        class="px-2 py-1 rounded-sm cursor-pointer text-xs bg-ui-elem hover:bg-ui-elem-hover text-ui-text-secondary border border-ui-border"
        onclick={tabResets[activeTab]}
      >
        Reset {activeTab.toLowerCase()} settings
      </button>
      <button
        class="font-bold px-3 py-1 rounded-sm cursor-pointer text-xs bg-ui-btn hover:bg-ui-btn-hover text-ui-btn-fg"
        onclick={onclose}
      >
        Close
      </button>
    </div>
  </div>
</div>
