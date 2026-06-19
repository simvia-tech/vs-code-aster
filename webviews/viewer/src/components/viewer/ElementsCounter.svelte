<script lang="ts">
  import { meshStats } from '../../lib/state';

  let stats = $derived($meshStats);

  function fmt(v: number): string {
    return v.toLocaleString();
  }
</script>

{#if stats}
  <div
    id="elementsCounter"
    class="absolute bottom-2 left-full ml-3 whitespace-nowrap pointer-events-none select-none text-[0.7rem] font-mono text-ui-text-secondary"
  >
    <div class="flex justify-between gap-3">
      <span>Elements</span>
      <span class="font-bold tabular-nums">{fmt(stats.elements)}</span>
    </div>
    <div class="flex justify-between gap-3">
      <span>Nodes</span>
      <span class="font-bold tabular-nums">{fmt(stats.nodes)}</span>
    </div>
  </div>
{/if}
