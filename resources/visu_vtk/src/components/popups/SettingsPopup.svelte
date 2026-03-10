<script lang="ts">
  import { settings } from '../../lib/state';
  import { GlobalSettings } from '../../lib/settings/GlobalSettings';
  import { CameraManager } from '../../lib/interaction/CameraManager';
  import { VisibilityManager } from '../../lib/commands/VisibilityManager';
  import { Controller } from '../../lib/Controller';
  import { CustomDropdown } from '../../lib/ui/CustomDropdown';
  import ChevronIcon from '../../icons/ChevronIcon.svelte';
  import type { EdgeMode } from '../../lib/state';

  let { onclose }: { onclose: () => void } = $props();

  const edgeModeOptions = [
    { value: 'threshold', label: 'Show edges when zooming (threshold)' },
    { value: 'gradual',   label: 'Show edges when zooming (gradual)' },
    { value: 'show',      label: 'Always show edges' },
    { value: 'hide',      label: 'Always hide edges' },
  ];

  const edgeModeDescriptions: Record<EdgeMode, string> = {
    gradual:   'Edges fade in as you zoom in, scaled by mesh density. When zoomed out, large meshes may appear very flat as outer edges are mostly hidden. Performance is impacted.',
    threshold: 'Edges appear abruptly at a zoom level based on mesh density. When zoomed out, large meshes may appear slightly flat as outer edges are hidden. Performance is not impacted.',
    show:      'Edges are always visible. Large meshes will appear almost entirely black when zoomed out. Performance is impacted.',
    hide:      'Edges are always hidden. All shapes will look slightly flat regardless of zoom level or mesh size.',
  };

  let edgeModeSelectEl: HTMLElement | null = $state(null);

  let hiddenOpacityPct = $derived(Math.round($settings.hiddenObjectOpacity * 100));
  let edgeThresholdDisplay = $derived(parseFloat(($settings.edgeThresholdMultiplier).toFixed(2)));
  let edgeModeLabel = $derived(edgeModeOptions.find((o) => o.value === $settings.edgeMode)?.label ?? $settings.edgeMode);
  let edgeModeDesc = $derived(edgeModeDescriptions[$settings.edgeMode] ?? '');
  let showThresholdSection = $derived($settings.edgeMode === 'threshold');

  $effect(() => {
    if (!edgeModeSelectEl) return;
    const dd = new CustomDropdown(
      edgeModeSelectEl,
      edgeModeOptions,
      (value) => applyEdgeMode(value as EdgeMode),
      () => GlobalSettings.Instance.edgeMode,
    );
    return () => {};
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

  function resetSettings() {
    const defaults = { hiddenObjectOpacity: 0, edgeMode: 'threshold' as EdgeMode, edgeThresholdMultiplier: 1 };
    GlobalSettings.Instance.hiddenObjectOpacity = defaults.hiddenObjectOpacity;
    GlobalSettings.Instance.edgeMode = defaults.edgeMode;
    GlobalSettings.Instance.edgeThresholdMultiplier = defaults.edgeThresholdMultiplier;
    settings.set(defaults);
    VisibilityManager.Instance.applyHiddenObjectOpacity();
    if (CameraManager.Instance.faceGroups) {
      CameraManager.Instance.refreshEdgeVisibility();
    }
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: defaults,
    });
  }
</script>

<div
  class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-2/3 max-h-2/3 rounded shadow-lg backdrop-blur-lg p-8 flex flex-col"
  style="background: var(--ui-popup-bg); color: var(--ui-fg); border: 1px solid var(--ui-border)"
  onclick={(e) => e.stopPropagation()}
  role="document"
>
  <span class="font-bold text-base">Settings</span>

  <div class="flex flex-col space-y-4 mt-4 pr-2 overflow-y-auto grow">
    <div class="flex flex-col space-y-1.5">
      <label class="text-sm font-semibold">Edge display</label>
      <div
        bind:this={edgeModeSelectEl}
        class="w-full text-xs px-2 py-1.5 rounded-sm cursor-pointer flex items-center justify-between gap-2 select-none"
        style="background: var(--ui-element-bg); color: var(--ui-fg); border: 1px solid var(--ui-border)"
        onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--ui-element-bg-hover)'; }}
        onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--ui-element-bg)'; }}
        role="button"
        tabindex="0"
      >
        <span class="truncate">{edgeModeLabel}</span>
        <ChevronIcon class="size-3 shrink-0" />
      </div>
      <span class="text-xs" style="color: var(--ui-text-secondary)">{edgeModeDesc}</span>
      {#if showThresholdSection}
        <div class="flex flex-col space-y-1.5 pt-0.5">
          <div class="flex items-center justify-between">
            <label class="text-xs font-medium">Threshold sensitivity</label>
            <span class="text-xs" style="color: var(--ui-text-secondary)">{edgeThresholdDisplay}×</span>
          </div>
          <input
            type="range"
            min="25"
            max="500"
            step="5"
            value={Math.round($settings.edgeThresholdMultiplier * 100)}
            class="w-full cursor-pointer accent-current focus:outline-none"
            oninput={onEdgeThresholdInput}
          />
          <span class="text-xs" style="color: var(--ui-text-secondary)">Higher values show edges from farther away.</span>
        </div>
      {/if}
    </div>

    <div class="flex flex-col space-y-1.5">
      <div class="flex items-center justify-between">
        <label class="text-sm font-semibold">Hidden objects opacity</label>
        <span class="text-xs" style="color: var(--ui-text-secondary)">{hiddenOpacityPct}%</span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        step="1"
        value={hiddenOpacityPct}
        class="w-full cursor-pointer accent-current focus:outline-none"
        oninput={onHiddenOpacityInput}
      />
      <span class="text-xs" style="color: var(--ui-text-secondary)">
        When hiding an object with the eye button, it can remain slightly visible as a ghost.
      </span>
    </div>
  </div>

  <div class="mt-4 flex justify-between items-center">
    <button
      class="px-3 py-1 rounded-sm cursor-pointer text-sm"
      style="background: var(--ui-element-bg); color: var(--ui-fg); border: 1px solid var(--ui-border)"
      onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'color-mix(in srgb, var(--ui-fg) 15%, transparent)'; }}
      onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--ui-element-bg)'; }}
      onclick={resetSettings}
    >
      Reset defaults
    </button>
    <button
      class="font-bold px-3 py-1 rounded-sm cursor-pointer"
      style="background: var(--ui-btn-bg); color: var(--ui-btn-fg)"
      onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--ui-btn-hover-bg)'; }}
      onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--ui-btn-bg)'; }}
      onclick={onclose}
    >
      Close
    </button>
  </div>
</div>
