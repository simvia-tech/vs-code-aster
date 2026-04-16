<script lang="ts">
  import { settings, boundingBoxDimensions } from '../../lib/state';

  function fmt(v: number): string {
    if (!isFinite(v)) return '—';
    const abs = Math.abs(v);
    if (abs === 0) return '0';
    if (abs >= 10000 || abs < 0.01) return v.toExponential(2);
    return v.toPrecision(4);
  }

  let dims = $derived($boundingBoxDimensions);
  let hidden = $derived(!($settings.showBoundingBox && dims));
</script>

{#if dims}
  <div
    id="bboxLabelOrigin"
    class="absolute pointer-events-none text-[0.7rem] font-mono font-bold text-ui-text-secondary select-none -translate-x-1/2 -translate-y-1/2"
    class:hidden
  >
    0
  </div>
  <div
    id="bboxLabelX"
    class="absolute pointer-events-none text-[0.7rem] font-mono font-bold text-red-500 select-none -translate-x-1/2 -translate-y-1/2"
    class:hidden
  >
    X: {fmt(dims.x)}
  </div>
  <div
    id="bboxLabelY"
    class="absolute pointer-events-none text-[0.7rem] font-mono font-bold text-green-500 select-none -translate-x-1/2 -translate-y-1/2"
    class:hidden
  >
    Y: {fmt(dims.y)}
  </div>
  <div
    id="bboxLabelZ"
    class="absolute pointer-events-none text-[0.7rem] font-mono font-bold text-blue-500 select-none -translate-x-1/2 -translate-y-1/2"
    class:hidden
  >
    Z: {fmt(dims.z)}
  </div>
{/if}
