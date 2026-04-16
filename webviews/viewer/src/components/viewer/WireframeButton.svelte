<script lang="ts">
  import { settings } from '../../lib/state';
  import { GlobalSettings } from '../../lib/settings/GlobalSettings';
  import { CameraManager } from '../../lib/interaction/CameraManager';
  import { Controller } from '../../lib/Controller';
  import WireframeIcon from '../../icons/WireframeIcon.svelte';

  function toggle() {
    const showWireframe = !$settings.showWireframe;
    GlobalSettings.Instance.showWireframe = showWireframe;
    settings.update((s) => ({ ...s, showWireframe }));
    CameraManager.Instance.setWireframeMode(showWireframe);
    Controller.Instance.getVSCodeAPI().postMessage({
      type: 'saveSettings',
      settings: { showWireframe },
    });
  }
</script>

<button
  title={$settings.showWireframe ? 'Switch to surface rendering' : 'Switch to wireframe rendering'}
  class="size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {$settings.showWireframe
    ? 'bg-ui-elem text-ui-link'
    : 'text-ui-text-secondary hover:bg-ui-elem'}"
  onclick={toggle}
>
  <WireframeIcon class="size-3.5" />
</button>
