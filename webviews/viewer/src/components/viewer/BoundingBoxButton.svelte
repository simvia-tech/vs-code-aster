<script lang="ts">
  import { settings } from '../../lib/state';
  import { GlobalSettings } from '../../lib/settings/GlobalSettings';
  import { CameraManager } from '../../lib/interaction/CameraManager';
  import { Controller } from '../../lib/Controller';
  import BoundingBoxIcon from '../../icons/BoundingBoxIcon.svelte';

  function toggle() {
    const showBoundingBox = !$settings.showBoundingBox;
    GlobalSettings.Instance.showBoundingBox = showBoundingBox;
    settings.update((s) => ({ ...s, showBoundingBox }));
    CameraManager.Instance.setBoundingBoxVisible(showBoundingBox);
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { showBoundingBox },
    });
  }
</script>

<button
  class="group relative size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {$settings.showBoundingBox
    ? 'bg-ui-elem text-ui-link'
    : 'text-ui-text-secondary hover:bg-ui-elem'}"
  onclick={toggle}
>
  <BoundingBoxIcon class="size-3.5" />
  <span
    class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 hidden group-hover:inline whitespace-nowrap text-ui-text-secondary text-xs"
  >
    Bounding box
  </span>
</button>
