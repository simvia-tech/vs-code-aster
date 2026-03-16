<script lang="ts">
  import { loadingProgress, loadingMessage } from '../../lib/state';
</script>

<div
  class="fixed inset-0 flex flex-col items-center justify-center gap-3 pointer-events-none text-ui-text-secondary"
>
  <div class="h-0.5 w-48 overflow-hidden rounded-full bg-ui-text-muted/20">
    <div
      class="h-full rounded-full bg-ui-text-muted"
      style="width: {$loadingProgress * 100}%"
    ></div>
  </div>
  <span class="text-xs">{$loadingMessage || 'Loading...'}</span>
</div>
