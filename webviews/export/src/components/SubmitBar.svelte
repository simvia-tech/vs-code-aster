<script lang="ts">
  interface Props {
    canSubmit: boolean;
    onSubmit: () => void;
    onCancel: () => void;
  }

  let { canSubmit, onSubmit, onCancel }: Props = $props();
</script>

<div class="mt-8 flex items-center justify-end gap-2">
  <button
    type="button"
    class="px-4 py-1.5 rounded bg-ui-elem hover:bg-ui-elem-hover text-ui-fg text-sm"
    onclick={onCancel}
  >
    Cancel
  </button>
  <button
    type="button"
    class="px-4 py-1.5 rounded bg-ui-btn hover:bg-ui-btn-hover text-ui-btn-fg text-sm font-semibold disabled:bg-ui-elem disabled:text-ui-text-muted disabled:cursor-not-allowed"
    disabled={!canSubmit}
    onclick={onSubmit}
  >
    Create
  </button>
</div>
