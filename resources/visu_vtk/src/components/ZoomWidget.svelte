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
    const dropdown = new CustomDropdown(
      zoomTriggerEl,
      [
        { value: '0.5', label: '0.5×' },
        { value: '1', label: '1×' },
        { value: '1.5', label: '1.5×' },
        { value: '2', label: '2×' },
        { value: '5', label: '5×' },
        { value: '10', label: '10×' },
      ],
      (value) => CameraManager.Instance.setZoom(parseFloat(value)),
      null,
      { align: 'right' }
    );
    return () => dropdown.close();
  });
</script>

<div
  id="zoomWidget"
  class="absolute bottom-2 z-10 -translate-x-1/2 flex items-stretch rounded-full overflow-hidden"
  style="left: 50%; background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)"
>
  <div
    id="zoomTrigger"
    bind:this={zoomTriggerEl}
    class="cursor-pointer select-none flex items-center gap-1.5 pl-2.5 py-1.5 transition-colors hover:bg-ui-elem-hover {$isAtDefaultZoom
      ? 'pr-2.5'
      : 'pr-0.75'}"
    style="color: var(--ui-text-secondary)"
    role="button"
    tabindex="0"
  >
    <ZoomIcon class="size-3.5" />
    <span id="zoomIndicator" class="text-xs font-mono leading-none">{zoomText}</span>
  </div>
  {#if !$isAtDefaultZoom}
    <button
      title="Reset zoom"
      class="pl-0.75 pr-2 cursor-pointer flex items-center justify-center transition-colors hover:bg-ui-elem-hover"
      style="color: var(--ui-text-secondary)"
      onclick={() => CameraManager.Instance.resetZoom()}
    >
      <ResetIcon class="size-3.5 p-px stroke-[2.5]" />
    </button>
  {/if}
</div>
