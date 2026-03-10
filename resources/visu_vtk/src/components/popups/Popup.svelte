<script lang="ts">
  let {
    onclose,
    children,
  }: {
    onclose: () => void;
    children: any;
  } = $props();
</script>

<div
  class="fixed inset-0 z-10 bg-black/20 backdrop-blur-xs"
  role="dialog"
  aria-modal="true"
  onclick={onclose}
>
  {@render children()}
</div>
