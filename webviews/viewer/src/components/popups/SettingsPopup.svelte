<script lang="ts">
  import { settings } from '../../lib/state';
  import { GlobalSettings } from '../../lib/settings/GlobalSettings';
  import { CameraManager } from '../../lib/interaction/CameraManager';
  import { VisibilityManager } from '../../lib/commands/VisibilityManager';
  import { Controller } from '../../lib/Controller';
  import { CustomDropdown } from '../../lib/ui/CustomDropdown';
  import ChevronIcon from '../../icons/ChevronIcon.svelte';
  import Toggle from '../Toggle.svelte';
  import type { EdgeMode } from '../../lib/state';

  let { onclose }: { onclose: () => void } = $props();

  const tabs = ['Edges', 'Visibility', 'Display'] as const;
  type Tab = (typeof tabs)[number];
  let activeTab = $state<Tab>('Edges');

  const edgeModeOptions = [
    { value: 'threshold', label: 'Show edges when zooming (threshold)' },
    { value: 'gradual', label: 'Show edges when zooming (gradual)' },
    { value: 'show', label: 'Always show edges' },
    { value: 'hide', label: 'Always hide edges' },
  ];

  const edgeModeDescriptions: Record<EdgeMode, string> = {
    gradual:
      'Edges fade in as you zoom in, scaled by mesh density. When zoomed out, large meshes may appear very flat as outer edges are mostly hidden. Performance is impacted.',
    threshold:
      'Edges appear abruptly at a zoom level based on mesh density. When zoomed out, large meshes may appear slightly flat as outer edges are hidden. Performance is not impacted.',
    show: 'Edges are always visible. Large meshes will appear almost entirely black when zoomed out. Performance is impacted.',
    hide: 'Edges are always hidden. All shapes will look slightly flat regardless of zoom level or mesh size.',
  };

  let edgeModeSelectEl: HTMLElement | null = $state(null);

  let hiddenOpacityPct = $derived(Math.round($settings.hiddenObjectOpacity * 100));
  let edgeThresholdDisplay = $derived(parseFloat($settings.edgeThresholdMultiplier.toFixed(2)));
  let edgeModeLabel = $derived(
    edgeModeOptions.find((o) => o.value === $settings.edgeMode)?.label ?? $settings.edgeMode
  );
  let edgeModeDesc = $derived(edgeModeDescriptions[$settings.edgeMode] ?? '');
  let showThresholdSection = $derived($settings.edgeMode === 'threshold');
  let groupTransparencyPct = $derived(Math.round($settings.groupTransparency * 100));

  $effect(() => {
    if (!edgeModeSelectEl) return;
    const dropdown = new CustomDropdown(
      edgeModeSelectEl,
      edgeModeOptions,
      (value) => applyEdgeMode(value as EdgeMode),
      () => GlobalSettings.Instance.edgeMode
    );
    return () => dropdown.close();
  });

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
  const VISIBILITY_DEFAULTS = {
    hiddenObjectOpacity: 0,
    groupTransparency: 0.2,
  };
  const DISPLAY_DEFAULTS = { showOrientationWidget: true };

  function resetEdgesTab() {
    GlobalSettings.Instance.edgeMode = EDGE_DEFAULTS.edgeMode;
    GlobalSettings.Instance.edgeThresholdMultiplier = EDGE_DEFAULTS.edgeThresholdMultiplier;
    settings.update((s) => ({ ...s, ...EDGE_DEFAULTS }));
    CameraManager.Instance.refreshEdgeVisibility();
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: EDGE_DEFAULTS,
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
      ...VISIBILITY_DEFAULTS,
      ...DISPLAY_DEFAULTS,
    };
    GlobalSettings.Instance.hiddenObjectOpacity = defaults.hiddenObjectOpacity;
    GlobalSettings.Instance.edgeMode = defaults.edgeMode;
    GlobalSettings.Instance.edgeThresholdMultiplier = defaults.edgeThresholdMultiplier;
    GlobalSettings.Instance.groupTransparency = defaults.groupTransparency;
    GlobalSettings.Instance.showOrientationWidget = defaults.showOrientationWidget;
    settings.update((s) => ({ ...s, ...defaults }));
    VisibilityManager.Instance.applyHiddenObjectOpacity();
    VisibilityManager.Instance.applyGroupTransparency();
    CameraManager.Instance.refreshEdgeVisibility();
    CameraManager.Instance.setOrientationWidgetVisible(true);
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: defaults,
    });
  }

  const tabResets: Record<Tab, () => void> = {
    Edges: resetEdgesTab,
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
    <div class="grow pr-1">
      {#if activeTab === 'Edges'}
        <div class="flex flex-col space-y-2">
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-medium">Edge rendering mode</span>
            {@render tip(
              'Choose when mesh edges are visible: always, never, or only when zooming in. Threshold mode shows edges abruptly at a zoom level; gradual mode fades them in (may impact performance on dense meshes).'
            )}
          </div>
          <div
            bind:this={edgeModeSelectEl}
            class="w-full text-xs px-2 py-1.5 rounded-sm cursor-pointer flex items-center justify-between gap-2 select-none bg-ui-elem hover:bg-ui-elem-hover text-ui-fg border border-ui-border"
            role="button"
            tabindex="0"
          >
            <span class="truncate">{edgeModeLabel}</span>
            <ChevronIcon class="size-3 shrink-0" />
          </div>
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
        <div class="flex flex-col space-y-2">
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
