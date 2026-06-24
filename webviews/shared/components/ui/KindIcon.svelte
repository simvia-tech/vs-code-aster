<script lang="ts">
  // Mesh-group topology glyph, reusing the exact icons the 3D viewer uses for
  // its groups (volume / surface / edge / node) so the two webviews match.
  import VolumeIcon from '../icons/VolumeIcon.svelte';
  import FaceIcon from '../icons/FaceIcon.svelte';
  import EdgeIcon from '../icons/EdgeIcon.svelte';
  import NodeIcon from '../icons/NodeIcon.svelte';

  let { kind, class: className = 'size-3.5 shrink-0 opacity-80' }: {
    kind: string;
    class?: string;
  } = $props();
</script>

{#if kind === 'volume'}
  <VolumeIcon class={className} />
{:else if kind === 'surface'}
  <FaceIcon class={className} />
{:else if kind === 'edge'}
  <EdgeIcon class={className} />
{:else if kind === 'node'}
  <NodeIcon class={className} />
{/if}
