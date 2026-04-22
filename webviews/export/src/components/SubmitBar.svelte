<script lang="ts">
  interface Props {
    canSubmit: boolean;
    submitLabel?: string;
    errorCount?: number;
    warningCount?: number;
    onSubmit: () => void;
    onCancel: () => void;
    onScrollToErrors?: () => void;
    onScrollToWarnings?: () => void;
  }

  let {
    canSubmit,
    submitLabel = 'Create',
    errorCount = 0,
    warningCount = 0,
    onSubmit,
    onCancel,
    onScrollToErrors,
    onScrollToWarnings,
  }: Props = $props();
</script>

<div
  class="sticky bottom-0 -mx-8 -mb-8 mt-auto pt-3 px-8 pb-3 z-30 flex items-center justify-between gap-3 border-t border-ui-border"
  style="background: color-mix(in srgb, var(--ui-bg) 92%, transparent); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px)"
>
  <div class="flex items-center gap-4 text-xs">
    {#if errorCount > 0}
      <button
        type="button"
        class="pill pill-error flex items-center gap-1.5 font-medium cursor-pointer focus:outline-none rounded px-2 py-1 -mx-2"
        style="color: var(--vscode-inputValidation-errorBorder, #d45858)"
        aria-label={`Jump to ${errorCount} error${errorCount === 1 ? '' : 's'}`}
        onclick={onScrollToErrors}
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        {errorCount}
        {errorCount === 1 ? 'error' : 'errors'}
      </button>
    {/if}
    {#if warningCount > 0}
      <button
        type="button"
        class="pill pill-warning flex items-center gap-1.5 font-medium cursor-pointer focus:outline-none rounded px-2 py-1 -mx-2"
        style="color: var(--vscode-editorWarning-foreground, #cca700)"
        aria-label={`Jump to ${warningCount} warning${warningCount === 1 ? '' : 's'}`}
        onclick={onScrollToWarnings}
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
          <path d="M12 9v4" />
          <path d="M12 17h.01" />
        </svg>
        {warningCount}
        {warningCount === 1 ? 'warning' : 'warnings'}
      </button>
    {/if}
  </div>

  <div class="flex items-center gap-2">
    <button
      type="button"
      class="px-4 py-1.5 rounded bg-ui-elem hover:bg-ui-elem-hover text-ui-fg text-sm cursor-pointer"
      onclick={onCancel}
    >
      Cancel
    </button>
    <button
      type="button"
      class="px-4 py-1.5 rounded bg-ui-btn hover:bg-ui-btn-hover text-ui-btn-fg text-sm font-semibold cursor-pointer disabled:bg-ui-elem disabled:text-ui-text-muted disabled:cursor-not-allowed"
      disabled={!canSubmit}
      onclick={onSubmit}
    >
      {submitLabel}
    </button>
  </div>
</div>

<style>
  .pill-error:hover,
  .pill-error:focus-visible {
    background: color-mix(
      in srgb,
      var(--vscode-inputValidation-errorBorder, #d45858) 16%,
      transparent
    );
  }
  .pill-warning:hover,
  .pill-warning:focus-visible {
    background: color-mix(
      in srgb,
      var(--vscode-editorWarning-foreground, #cca700) 16%,
      transparent
    );
  }
</style>
