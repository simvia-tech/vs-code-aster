<script lang="ts">
  import { zoomRatio, isAtDefaultZoom } from '../lib/state';
  import { CameraManager } from '../lib/interaction/CameraManager';
  import { CustomDropdown } from '../lib/ui/CustomDropdown';
  import ZoomIcon from '../icons/ZoomIcon.svelte';
  import ResetIcon from '../icons/ResetIcon.svelte';

  let zoomTriggerEl: HTMLElement | null = $state(null);

  let zoomText = $derived.by(() => {
    const ratio = $zoomRatio;
    if (ratio >= 10) return `${Math.round(ratio)}×`;
    if (ratio >= 1) return `${ratio.toFixed(1)}×`;
    return `${ratio.toFixed(2)}×`;
  });

  $effect(() => {
    if (!zoomTriggerEl) return;
    new CustomDropdown(
      zoomTriggerEl,
      [
        { value: '0.5', label: '0.5×' },
        { value: '1',   label: '1×'   },
        { value: '1.5', label: '1.5×' },
        { value: '2',   label: '2×'   },
        { value: '5',   label: '5×'   },
        { value: '10',  label: '10×'  },
      ],
      (value) => CameraManager.Instance.setZoom(parseFloat(value)),
      null,
      { align: 'right' },
    );
    return () => {};
  });
</script>

<div
  id="zoomWidget"
  class="absolute bottom-2 z-10 -translate-x-1/2 flex items-center gap-1.5 px-2.5 py-1 rounded-full"
  style="left: 50%; background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)"
>
  <ZoomIcon class="size-3 text-[var(--ui-text-secondary)]" />
  <div
    id="zoomTrigger"
    bind:this={zoomTriggerEl}
    class="cursor-pointer select-none px-1 py-0.5 rounded"
    style="color: var(--ui-text-secondary)"
    onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'color-mix(in srgb, var(--ui-fg) 7%, transparent)'; }}
    onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = ''; }}
    role="button"
    tabindex="0"
  >
    <span id="zoomIndicator" class="text-xs font-mono">{zoomText}</span>
  </div>
  {#if !$isAtDefaultZoom}
    <button
      title="Reset zoom"
      class="size-3.5 cursor-pointer flex items-center justify-center opacity-50 hover:opacity-100"
      style="color: var(--ui-fg)"
      onclick={() => CameraManager.Instance.resetZoom()}
    >
      <ResetIcon class="size-3.5" />
    </button>
  {/if}
</div>
