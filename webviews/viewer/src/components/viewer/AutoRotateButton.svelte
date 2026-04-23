<script lang="ts">
  import {
    sessionAutoRotate,
    autoRotateSessionSpeed,
    autoRotateSessionReverse,
    openToolbarPopover,
  } from '../../lib/state';
  import { CameraManager } from '../../lib/interaction/CameraManager';
  import AutoRotateIcon from '../../icons/AutoRotateIcon.svelte';
  import Toggle from '../ui/Toggle.svelte';

  const POPOVER_ID = 'autoRotate';
  let popoverOpen = $derived($openToolbarPopover === POPOVER_ID);
  let wrapper: HTMLDivElement | undefined = $state();

  function toggle() {
    const next = !$sessionAutoRotate;
    sessionAutoRotate.set(next);
    CameraManager.Instance.setAutoRotate(next);
  }

  function onContextMenu(e: MouseEvent) {
    e.preventDefault();
    openToolbarPopover.set(popoverOpen ? null : POPOVER_ID);
  }

  function onSpeedInput(e: Event) {
    const speed = parseInt((e.target as HTMLInputElement).value, 10);
    autoRotateSessionSpeed.set(speed);
    CameraManager.Instance.setAutoRotateSpeed(speed);
  }

  function toggleReverse() {
    const reverse = !$autoRotateSessionReverse;
    autoRotateSessionReverse.set(reverse);
    CameraManager.Instance.setAutoRotateReverse(reverse);
  }

  function onDocClick(e: MouseEvent) {
    if (!popoverOpen) return;
    if (wrapper && !wrapper.contains(e.target as Node)) {
      openToolbarPopover.set(null);
    }
  }
</script>

<svelte:document onclick={onDocClick} />

<div bind:this={wrapper} class="relative flex items-stretch">
  <button
    class="group relative size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {$sessionAutoRotate
      ? 'bg-ui-elem text-ui-link'
      : 'text-ui-text-secondary hover:bg-ui-elem'}"
    onclick={toggle}
    oncontextmenu={onContextMenu}
  >
    <AutoRotateIcon class="size-3.5" />
    {#if !popoverOpen}
      <span
        class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 hidden group-hover:inline whitespace-nowrap text-ui-text-secondary text-xs"
      >
        Auto-rotate (right-click for options)
      </span>
    {/if}
  </button>

  {#if popoverOpen}
    <div
      class="absolute top-full left-0 mt-1 z-20 w-60 rounded shadow-lg border border-ui-border bg-ui-popup-bg p-3 text-ui-fg flex flex-col gap-3"
      role="dialog"
    >
      <div class="flex flex-col space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium">Rotation speed</span>
          <span class="text-xs text-ui-text-secondary">{$autoRotateSessionSpeed}°/s</span>
        </div>
        <input
          type="range"
          min="5"
          max="180"
          step="1"
          value={$autoRotateSessionSpeed}
          class="w-full cursor-pointer focus:outline-none [accent-color:var(--vscode-textLink-foreground,#0078d4)]"
          oninput={onSpeedInput}
        />
      </div>
      <div class="flex items-center gap-3">
        <Toggle
          checked={$autoRotateSessionReverse}
          onclick={toggleReverse}
          ariaLabel="Reverse rotation"
        />
        <span class="text-xs font-medium">Reverse direction</span>
      </div>
      <span class="text-xs text-ui-text-secondary leading-snug">
        Changes here apply to the current session only. Set defaults in Settings → Toolbar.
      </span>
    </div>
  {/if}
</div>
