<script lang="ts">
  import { sessionShowWireframe } from '../../lib/state';
  import { CameraManager } from '../../lib/interaction/CameraManager';
  import WireframeIcon from '../../icons/WireframeIcon.svelte';

  function toggle() {
    const next = !$sessionShowWireframe;
    sessionShowWireframe.set(next);
    CameraManager.Instance.setWireframeMode(next);
  }
</script>

<button
  class="group relative size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {$sessionShowWireframe
    ? 'bg-ui-elem text-ui-link'
    : 'text-ui-text-secondary hover:bg-ui-elem'}"
  onclick={toggle}
>
  <WireframeIcon class="size-3.5" />
  <span
    class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 hidden group-hover:inline whitespace-nowrap text-ui-text-secondary text-xs"
  >
    Wireframe
  </span>
</button>
