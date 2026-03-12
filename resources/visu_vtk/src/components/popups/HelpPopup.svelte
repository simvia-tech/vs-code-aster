<script lang="ts">
  import ClearIcon from '../../icons/ClearIcon.svelte';
  import EyeIcon from '../../icons/EyeIcon.svelte';
  import FaceIcon from '../../icons/FaceIcon.svelte';
  import FilterIcon from '../../icons/FilterIcon.svelte';
  import MouseLeftIcon from '../../icons/MouseLeftIcon.svelte';
  import ObjectIcon from '../../icons/ObjectIcon.svelte';
  import MouseScrollIcon from '../../icons/MouseScrollIcon.svelte';
  import ResetIcon from '../../icons/ResetIcon.svelte';
  import SettingsIcon from '../../icons/SettingsIcon.svelte';
  import ZoomIcon from '../../icons/ZoomIcon.svelte';

  declare const __APP_VERSION__: string;

  let { onclose }: { onclose: () => void } = $props();

  const mainTabs = ['Camera', 'Objects', 'Groups', 'Settings', 'Files'] as const;
  const tabs = [...mainTabs, 'About'] as const;
  type Tab = typeof tabs[number];
  let activeTab = $state<Tab>('Camera');
</script>

<style>
  kbd {
    display: inline-flex;
    align-items: center;
    padding: 0.1rem 0.35rem 0.1rem 0.25rem;
    width: fit-content;
    font-size: 0.7rem;
    font-family: inherit;
    border-radius: 3px;
    border: 1px solid var(--ui-border);
    background: var(--ui-element-bg);
    line-height: 1.4;
    white-space: nowrap;
  }
</style>

<div
  id="helpPopup"
  class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 rounded shadow-lg backdrop-blur-lg flex overflow-hidden"
  style="width: min(52rem, 80vw); height: 70vh; background: var(--ui-popup-bg); color: var(--ui-fg); border: 1px solid var(--ui-border)"
  role="document"
>
  <nav class="flex flex-col py-4 shrink-0 w-36" style="border-right: 1px solid var(--ui-border)">
    <span class="font-bold text-sm px-4 pb-3" style="color: var(--ui-text-primary)">Help</span>
    {#each mainTabs as tab}
      <button
        class="text-left text-xs px-4 py-2 cursor-pointer transition-colors"
        style={activeTab === tab
          ? 'background: var(--ui-element-bg); color: var(--vscode-textLink-foreground, #0078d4); font-weight: 600;'
          : 'color: var(--ui-text-secondary);'}
        onmouseenter={(e) => { if (activeTab !== tab) (e.currentTarget as HTMLElement).style.background = 'var(--ui-element-bg)'; }}
        onmouseleave={(e) => { if (activeTab !== tab) (e.currentTarget as HTMLElement).style.background = ''; }}
        onclick={() => activeTab = tab}
      >
        {tab}
      </button>
    {/each}
    <div class="grow"></div>
    <button
      class="text-left text-xs px-4 py-2 cursor-pointer transition-colors"
      style={activeTab === 'About'
        ? 'background: var(--ui-element-bg); color: var(--vscode-textLink-foreground, #0078d4); font-weight: 600;'
        : 'color: var(--ui-text-secondary);'}
      onmouseenter={(e) => { if (activeTab !== 'About') (e.currentTarget as HTMLElement).style.background = 'var(--ui-element-bg)'; }}
      onmouseleave={(e) => { if (activeTab !== 'About') (e.currentTarget as HTMLElement).style.background = ''; }}
      onclick={() => activeTab = 'About'}
    >
      <span class="flex items-center justify-between gap-2">
        About
        <span style="color: {activeTab === 'About' ? 'var(--vscode-textLink-foreground, #0078d4)' : 'var(--ui-text-muted)'}; font-weight: 400; font-size: 0.6rem;">v{__APP_VERSION__}</span>
      </span>
    </button>
  </nav>

  <div class="flex flex-col flex-1 min-w-0 p-6">
    <div class="grow overflow-y-auto text-xs pr-1">

      {#if activeTab === 'Camera'}
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-center">
          <MouseLeftIcon class="size-5" /><span>Drag to rotate</span>
          <span class="inline-flex items-center gap-1"><kbd>Ctrl</kbd>+<MouseLeftIcon class="size-5" /></span><span>Drag to rotate around a single axis</span>
          <span class="inline-flex items-center gap-1"><kbd>Shift</kbd>+<MouseLeftIcon class="size-5" /></span><span>Drag to pan</span>
          <MouseScrollIcon class="size-5" /><span>Zoom in / out</span>
          <span class="inline-flex items-stretch rounded-full overflow-hidden text-[0.65rem]"
            style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)">
            <span class="flex items-center gap-1 pl-2 pr-1 py-1" style="background: var(--ui-element-bg-hover); color: var(--ui-fg)">
              <ZoomIcon class="size-3" /><span class="font-mono">2.0×</span>
            </span>
            <span class="pl-0.5 pr-1.5 flex items-center" style="color: var(--ui-text-muted)">
              <ResetIcon class="size-3 stroke-[2.5]" />
            </span>
          </span>
          <span>Open the zoom level selector to choose a preset</span>

          <span class="inline-flex items-stretch rounded-full overflow-hidden text-[0.65rem]"
            style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)">
            <span class="flex items-center gap-1 pl-2 pr-1 py-1" style="color: var(--ui-text-muted)">
              <ZoomIcon class="size-3" /><span class="font-mono">2.0×</span>
            </span>
            <span class="pl-0.5 pr-1.5 flex items-center" style="background: var(--ui-element-bg-hover); color: var(--ui-fg)">
              <ResetIcon class="size-3 stroke-[2.5]" />
            </span>
          </span>
          <span>Reset zoom to 1× — appears only when zoom ≠ 1×</span>
          <span class="inline-flex gap-1">
            <kbd class="text-red-600! font-bold">X</kbd>
            <kbd class="text-green-600! font-bold">Y</kbd>
            <kbd class="text-blue-500! font-bold">Z</kbd>
          </span>
          <span>Align camera along that axis — buttons at the bottom of the sidebar</span>
        </div>

      {:else if activeTab === 'Objects'}
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-center">
          <span class="inline-flex items-center gap-1 text-[0.65rem] pl-1 pr-0.5 py-0.5 rounded"
            style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)">
            <span style="color: var(--ui-text-muted)"><ObjectIcon class="size-3.5" /></span>
            <span class="px-2 font-bold rounded" style="background: var(--ui-element-bg-hover); color: var(--ui-fg)">mesh</span>
            <span class="size-3.5 flex items-center justify-center" style="color: var(--ui-text-muted); opacity: 0.4"><EyeIcon class="size-3" /></span>
          </span>
          <span>Click the name to <strong>collapse or expand</strong> its groups</span>

          <span class="inline-flex items-center gap-1 text-[0.65rem] pl-1 pr-0.5 py-0.5 rounded"
            style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)">
            <span style="color: var(--ui-text-muted)"><ObjectIcon class="size-3.5" /></span>
            <span class="px-2 font-bold" style="color: var(--ui-text-muted)">mesh</span>
            <span class="size-3.5 flex items-center justify-center rounded" style="background: var(--ui-element-bg-hover); color: var(--ui-fg)"><EyeIcon class="size-3" /></span>
          </span>
          <span>Click to <strong>show or hide</strong> an entire object</span>

          <span class="inline-flex items-center gap-1 text-[0.65rem] pl-1 pr-0.5 py-0.5 rounded"
            style="background: var(--ui-element-bg-hover); border: 1px solid var(--ui-border)">
            <span style="color: var(--ui-text-muted)"><ObjectIcon class="size-3.5" /></span>
            <span class="px-2 font-bold" style="color: var(--ui-fg)">mesh</span>
            <span class="size-3.5 flex items-center justify-center" style="color: var(--ui-text-muted); opacity: 0.4"><EyeIcon class="size-3" /></span>
          </span>
          <span>Right-click for more options — e.g. hide all other objects</span>
        </div>

      {:else if activeTab === 'Groups'}
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-center">
          <span class="relative inline-flex items-center text-[0.65rem] px-2 pt-0.5 pb-1 rounded-sm"
            style="background: var(--ui-element-bg-hover); color: var(--ui-fg); font-weight: 600; min-width: 4rem;">
            <span class="absolute left-1 top-0.5"><FaceIcon class="size-3.5" /></span>
            <span class="pl-4">group_A</span>
          </span>
          <span>Click a group to <strong>highlight</strong> it — the object becomes transparent so the group stands out. Click again to unhighlight.</span>

          <span class="w-fit inline-flex flex-col items-center rounded-sm overflow-hidden"
            style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)">
            <span class="size-5 flex items-center justify-center" style="background: var(--ui-element-bg-hover); color: var(--ui-fg)"><FilterIcon class="size-3" /></span>
            <span class="w-3/4 h-px" style="background: var(--ui-border)"></span>
            <span class="size-5 flex items-center justify-center" style="color: var(--ui-text-muted)"><ClearIcon class="size-3" /></span>
          </span>
          <span>Click to <strong>choose which groups appear</strong> in the sidebar — hidden groups remain visible in the 3D view</span>

          <span class="w-fit inline-flex flex-col items-center rounded-sm overflow-hidden"
            style="background: color-mix(in srgb, var(--ui-bg) 85%, transparent); border: 1px solid var(--ui-border)">
            <span class="size-5 flex items-center justify-center" style="color: var(--ui-text-muted)"><FilterIcon class="size-3" /></span>
            <span class="w-3/4 h-px" style="background: var(--ui-border)"></span>
            <span class="size-5 flex items-center justify-center" style="background: var(--ui-element-bg-hover); color: var(--ui-fg)"><ClearIcon class="size-3" /></span>
          </span>
          <span>Click to <strong>clear all highlights</strong></span>
        </div>

      {:else if activeTab === 'Settings'}
        <p class="mb-4">
          Open settings with <span class="inline-flex align-top mx-0.5"><SettingsIcon class="size-4" /></span> in the top-right corner.
        </p>
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-start">
          <span class="font-semibold">Edge display</span>
          <span>Choose when mesh edges are visible: always, never, or only when zooming in. Threshold mode shows edges abruptly at a zoom level; gradual mode fades them in (may impact performance on dense meshes)</span>
          <span class="font-semibold whitespace-nowrap">Hidden opacity</span>
          <span>How transparent hidden objects appear — at 0% they are fully invisible, above 0% they remain as ghosts</span>
        </div>

      {:else if activeTab === 'Files'}
        <div class="space-y-2" style="color: var(--ui-text-secondary)">
          <p><code>.med</code> mesh files are automatically converted to <code>.obj</code> when opened.</p>
          <p>Converted files are cached in a hidden <code>.visu_data/</code> folder in your workspace and reused on subsequent opens.</p>
        </div>

      {:else if activeTab === 'About'}
        <div class="space-y-3" style="color: var(--ui-text-secondary)">
          <p>This extension is made by <a href="https://simvia.tech" target="_blank" rel="noopener noreferrer" style="color: var(--vscode-textLink-foreground, #0078d4); text-decoration: underline;">Simvia</a>.</p>
          <p>Source code and issue tracker are available on <a href="https://github.com/simvia-tech/vs-code-aster" target="_blank" rel="noopener noreferrer" style="color: var(--vscode-textLink-foreground, #0078d4); text-decoration: underline;">GitHub</a>.</p>
        </div>
      {/if}

    </div>

    <div class="mt-4 flex justify-end">
      <button
        class="font-bold px-3 py-1 rounded-sm cursor-pointer text-xs bg-ui-btn hover:bg-ui-btn-hover"
        style="color: var(--ui-btn-fg)"
        onclick={onclose}
      >
        Close
      </button>
    </div>
  </div>
</div>
