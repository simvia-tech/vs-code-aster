<script lang="ts">
  import SettingsIcon from '../icons/SettingsIcon.svelte';
  import QuestionIcon from '../icons/QuestionIcon.svelte';

  let {
    onOpenSettings,
    onOpenHelp,
  }: {
    onOpenSettings: () => void;
    onOpenHelp: () => void;
  } = $props();
</script>

<div class="absolute right-2 top-2 z-10 flex flex-col items-center space-y-1">
  <button
    class="p-1.5 rounded-full cursor-pointer group flex items-center"
    style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent)"
    onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'color-mix(in srgb, var(--ui-bg) 100%, transparent)'; }}
    onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'color-mix(in srgb, var(--ui-bg) 85%, transparent)'; }}
    onclick={onOpenSettings}
  >
    <SettingsIcon class="size-4" />
    <span
      class="absolute right-full pr-1.5 hidden group-hover:inline whitespace-nowrap"
      style="color: var(--ui-text-secondary)"
    >
      Settings
    </span>
  </button>
  <button
    class="p-1.5 rounded-full cursor-pointer group flex items-center"
    style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent)"
    onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'color-mix(in srgb, var(--ui-bg) 100%, transparent)'; }}
    onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'color-mix(in srgb, var(--ui-bg) 85%, transparent)'; }}
    onclick={onOpenHelp}
  >
    <QuestionIcon class="size-4" />
    <span
      class="absolute right-full pr-1.5 hidden group-hover:inline whitespace-nowrap"
      style="color: var(--ui-text-secondary)"
    >
      Help
    </span>
  </button>
</div>
