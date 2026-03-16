<script lang="ts">
  import { zoomRatio, isAtDefaultZoom } from '../lib/state';
  import { CameraManager } from '../lib/interaction/CameraManager';
  import Dropdown from './Dropdown.svelte';
  import ZoomIcon from '../icons/ZoomIcon.svelte';
  import ResetIcon from '../icons/ResetIcon.svelte';

  let zoomText = $derived.by(() => {
    const ratio = $zoomRatio;
    if (ratio >= 10) return `${Math.round(ratio)}×`;
    if (ratio >= 1) return `${ratio.toFixed(1)}×`;
    return `${ratio.toFixed(2)}×`;
  });

  const zoomOptions = [
    { value: '0.5', label: '0.5×' },
    { value: '1', label: '1×' },
    { value: '1.5', label: '1.5×' },
    { value: '2', label: '2×' },
    { value: '5', label: '5×' },
    { value: '10', label: '10×' },
  ];
</script>

<div
  id="zoomWidget"
  class="absolute bottom-2 z-10 left-1/2 -translate-x-1/2 flex items-stretch rounded-full overflow-hidden bg-ui-muted border border-ui-border"
>
  <Dropdown
    options={zoomOptions}
    onSelect={(v) => CameraManager.Instance.setZoom(parseFloat(v))}
    align="right"
  >
    <div
      id="zoomTrigger"
      class="cursor-pointer select-none flex items-center gap-1.5 pl-2.5 py-1.5 transition-colors hover:bg-ui-elem-hover text-ui-text-secondary {$isAtDefaultZoom
        ? 'pr-2.5'
        : 'pr-0.75'}"
      role="button"
      tabindex="0"
    >
      <ZoomIcon class="size-3.5" />
      <span id="zoomIndicator" class="text-xs font-mono leading-none">{zoomText}</span>
    </div>
  </Dropdown>
  {#if !$isAtDefaultZoom}
    <button
      title="Reset zoom"
      class="pl-0.75 pr-2 cursor-pointer flex items-center justify-center transition-colors hover:bg-ui-elem-hover text-ui-text-secondary"
      onclick={() => CameraManager.Instance.resetZoom()}
    >
      <ResetIcon class="size-3.5 p-px stroke-[2.5]" />
    </button>
  {/if}
</div>
