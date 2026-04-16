<script lang="ts">
  import BoundingBoxButton from '../viewer/BoundingBoxButton.svelte';
  import WireframeButton from '../viewer/WireframeButton.svelte';
  import ScreenshotButton from '../viewer/ScreenshotButton.svelte';
</script>

<div
  id="topToolbar"
  class="absolute top-0 z-10 left-1/2 -translate-x-1/2 flex items-stretch rounded-b-sm border border-t-0 bg-ui-muted border-ui-border"
>
  <BoundingBoxButton />
  <div class="w-px bg-ui-border"></div>
  <WireframeButton />
  <div class="w-px bg-ui-border"></div>
  <ScreenshotButton />
</div>
