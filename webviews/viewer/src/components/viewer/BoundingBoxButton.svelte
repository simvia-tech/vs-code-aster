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
  title={$settings.showBoundingBox ? 'Hide bounding box' : 'Show bounding box with dimensions'}
  class="size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {$settings.showBoundingBox
    ? 'bg-ui-elem text-ui-link'
    : 'text-ui-text-secondary hover:bg-ui-elem'}"
  onclick={toggle}
>
  <BoundingBoxIcon class="size-3.5" />
</button>
