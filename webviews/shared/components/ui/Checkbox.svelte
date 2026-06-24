<script lang="ts">
  let {
    checked,
    label,
    hint = '',
    block = false,
    onchange,
  }: {
    checked: boolean;
    label: string;
    /** Optional trailing text (e.g. a group's topology kind). */
    hint?: string;
    /** Full-width row layout with padding + hover — the whole row is the
     * clickable label. Default is a compact inline checkbox. */
    block?: boolean;
    onchange: () => void;
  } = $props();
</script>

{#if block}
  <label
    class="flex w-full cursor-pointer items-center justify-between gap-3 px-2.5 py-1 hover:bg-ui-elem-hover"
  >
    <span class="flex items-center gap-1.5 text-sm">
      <input type="checkbox" class="cb" {checked} {onchange} />
      <span>{label}</span>
    </span>
    {#if hint}
      <span class="text-[0.65rem] opacity-60">{hint}</span>
    {/if}
  </label>
{:else}
  <label class="flex cursor-pointer items-center gap-1.5 text-sm">
    <input type="checkbox" class="cb" {checked} {onchange} />
    <span>{label}</span>
  </label>
{/if}

<style>
  .cb {
    appearance: none;
    width: 13px;
    height: 13px;
    flex-shrink: 0;
    border-radius: 3px;
    border: 1.5px solid var(--ui-text-secondary);
    cursor: pointer;
    position: relative;
    transition:
      background 0.1s,
      border-color 0.1s;
  }
  .cb:focus {
    outline: none;
  }
  .cb:checked {
    background: var(--ui-btn-bg);
    border-color: var(--ui-btn-bg);
  }
  .cb:checked::after {
    content: '';
    position: absolute;
    inset: 0;
    margin: auto;
    width: 4px;
    height: 7px;
    border-right: 1.5px solid var(--ui-btn-fg);
    border-bottom: 1.5px solid var(--ui-btn-fg);
    transform: translateY(-1px) rotate(45deg);
  }
</style>
