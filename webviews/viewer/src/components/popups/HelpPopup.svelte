<script lang="ts" module>
  declare const __APP_VERSION__: string;
</script>

<script lang="ts">
  import BoundingBoxIcon from '../../icons/BoundingBoxIcon.svelte';
  import ClearIcon from '../../icons/ClearIcon.svelte';
  import EdgeIcon from '../../icons/EdgeIcon.svelte';
  import EyeIcon from '../../icons/EyeIcon.svelte';
  import FaceIcon from '../../icons/FaceIcon.svelte';
  import FilterIcon from '../../icons/FilterIcon.svelte';
  import MouseLeftIcon from '../../icons/MouseLeftIcon.svelte';
  import NodeIcon from '../../icons/NodeIcon.svelte';
  import ObjectIcon from '../../icons/ObjectIcon.svelte';
  import MouseScrollIcon from '../../icons/MouseScrollIcon.svelte';
  import ResetIcon from '../../icons/ResetIcon.svelte';
  import ScreenshotIcon from '../../icons/ScreenshotIcon.svelte';
  import VolumeIcon from '../../icons/VolumeIcon.svelte';
  import WireframeIcon from '../../icons/WireframeIcon.svelte';
  import ZoomIcon from '../../icons/ZoomIcon.svelte';

  let { onclose }: { onclose: () => void } = $props();

  const mainTabs = ['Camera', 'Toolbar', 'Objects', 'Groups', 'Files'] as const;
  const tabs = [...mainTabs, 'About'] as const;
  type Tab = (typeof tabs)[number];
  let activeTab = $state<Tab>('Camera');
</script>

<div
  id="helpPopup"
  class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[min(52rem,80vw)] h-[70vh] rounded shadow-lg backdrop-blur-lg flex overflow-hidden bg-ui-popup-bg text-ui-fg border border-ui-border"
  role="document"
>
  <nav class="flex flex-col py-4 shrink-0 w-36 border-r border-ui-border">
    <span class="font-bold text-sm px-4 pb-3 text-ui-text-primary">Help</span>
    {#each mainTabs as tab}
      <button
        class="text-left text-xs px-4 py-2 cursor-pointer transition-colors hover:bg-ui-elem {activeTab ===
        tab
          ? 'bg-ui-elem text-ui-link font-semibold'
          : 'text-ui-text-secondary'}"
        onclick={() => (activeTab = tab)}
      >
        {tab}
      </button>
    {/each}
    <div class="grow"></div>
    <button
      class="text-left text-xs px-4 py-2 cursor-pointer transition-colors hover:bg-ui-elem {activeTab ===
      'About'
        ? 'bg-ui-elem text-ui-link font-semibold'
        : 'text-ui-text-secondary'}"
      onclick={() => (activeTab = 'About')}
    >
      <span class="flex items-center justify-between gap-2">
        About
        <span
          class="{activeTab === 'About'
            ? 'text-ui-link'
            : 'text-ui-text-muted'} font-normal text-[0.6rem]">v{__APP_VERSION__}</span
        >
      </span>
    </button>
  </nav>

  <div class="flex flex-col flex-1 min-w-0 p-6">
    <div class="grow overflow-y-auto text-xs pr-1">
      {#if activeTab === 'Camera'}
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-center">
          <MouseLeftIcon class="size-5" /><span>Drag to rotate</span>
          <span class="inline-flex items-center gap-1"
            ><kbd>Ctrl</kbd>+<MouseLeftIcon class="size-5" /></span
          ><span>Drag to rotate around a single axis</span>
          <span class="inline-flex items-center gap-1"
            ><kbd>Shift</kbd>+<MouseLeftIcon class="size-5" /></span
          ><span>Drag to pan</span>
          <MouseScrollIcon class="size-5" /><span>Zoom in / out</span>
          <span
            class="inline-flex items-stretch rounded-full overflow-hidden text-[0.65rem] bg-ui-muted border border-ui-border"
          >
            <span class="flex items-center gap-1 pl-2 pr-1 py-1 bg-ui-elem-hover text-ui-fg">
              <ZoomIcon class="size-3" /><span class="font-mono">2.0×</span>
            </span>
            <span class="pl-0.5 pr-1.5 flex items-center text-ui-text-muted">
              <ResetIcon class="size-3 stroke-[2.5]" />
            </span>
          </span>
          <span>Open the zoom level selector to choose a preset</span>

          <span
            class="inline-flex items-stretch rounded-full overflow-hidden text-[0.65rem] bg-ui-muted border border-ui-border"
          >
            <span class="flex items-center gap-1 pl-2 pr-1 py-1 text-ui-text-muted">
              <ZoomIcon class="size-3" /><span class="font-mono">2.0×</span>
            </span>
            <span class="pl-0.5 pr-1.5 flex items-center bg-ui-elem-hover text-ui-fg">
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
      {:else if activeTab === 'Toolbar'}
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-center">
          <span
            class="inline-flex items-center justify-center size-6 rounded-sm bg-ui-muted border border-ui-border text-ui-text-secondary stroke-[1.75]"
          >
            <BoundingBoxIcon class="size-3.5" />
          </span>
          <span
            >Toggle a <strong>bounding box</strong> with colored axes (<span
              class="text-red-500 font-bold">X</span
            >
            <span class="text-green-500 font-bold">Y</span>
            <span class="text-blue-500 font-bold">Z</span>), corner dots, and dimension labels to
            quickly read the characteristic size of the structure</span
          >

          <span
            class="inline-flex items-center justify-center size-6 rounded-sm bg-ui-muted border border-ui-border text-ui-text-secondary stroke-[1.75]"
          >
            <WireframeIcon class="size-3.5" />
          </span>
          <span
            >Switch between <strong>solid surface</strong> and <strong>wireframe</strong> rendering to
            inspect mesh density</span
          >

          <span
            class="inline-flex items-center justify-center size-6 rounded-sm bg-ui-muted border border-ui-border text-ui-text-secondary stroke-[1.75]"
          >
            <ScreenshotIcon class="size-3.5" />
          </span>
          <span
            ><strong>Left click</strong> — save the 3D view as PNG next to your file &amp; copy to
            clipboard. <strong>Right click</strong> — capture the full viewer including the sidebar.</span
          >
        </div>
      {:else if activeTab === 'Objects'}
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-center">
          <span
            class="inline-flex items-center gap-1 text-[0.65rem] pl-1 pr-0.5 py-0.5 rounded bg-ui-muted border border-ui-border"
          >
            <span class="text-ui-text-muted"><ObjectIcon class="size-3.5" /></span>
            <span class="px-2 font-bold rounded bg-ui-elem-hover text-ui-fg">mesh</span>
            <span class="size-3.5 flex items-center justify-center text-ui-text-muted opacity-40"
              ><EyeIcon class="size-3" /></span
            >
          </span>
          <span>Click the name to <strong>collapse or expand</strong> its groups</span>

          <span
            class="inline-flex items-center gap-1 text-[0.65rem] pl-1 pr-0.5 py-0.5 rounded bg-ui-muted border border-ui-border"
          >
            <span class="text-ui-text-muted"><ObjectIcon class="size-3.5" /></span>
            <span class="px-2 font-bold text-ui-text-muted">mesh</span>
            <span
              class="size-3.5 flex items-center justify-center rounded bg-ui-elem-hover text-ui-fg"
              ><EyeIcon class="size-3" /></span
            >
          </span>
          <span>Click to <strong>show or hide</strong> an entire object</span>

          <span
            class="inline-flex items-center gap-1 text-[0.65rem] pl-1 pr-0.5 py-0.5 rounded bg-ui-elem-hover border border-ui-border"
          >
            <span class="text-ui-text-muted"><ObjectIcon class="size-3.5" /></span>
            <span class="px-2 font-bold text-ui-fg">mesh</span>
            <span class="size-3.5 flex items-center justify-center text-ui-text-muted opacity-40"
              ><EyeIcon class="size-3" /></span
            >
          </span>
          <span>Right-click for more options — e.g. hide all other objects</span>
        </div>
      {:else if activeTab === 'Groups'}
        <div class="grid grid-cols-[auto_1fr] gap-x-5 gap-y-3 items-center">
          <span class="font-semibold text-ui-text-primary col-span-2">Group types</span>

          <span class="inline-flex items-center justify-center size-5 text-ui-text-secondary">
            <VolumeIcon class="size-3.5" />
          </span>
          <span
            ><strong>Volume group</strong> — the skin of a 3D sub-domain, rendered as its bounding surface.</span
          >

          <span class="inline-flex items-center justify-center size-5 text-ui-text-secondary">
            <FaceIcon class="size-3.5" />
          </span>
          <span><strong>Face group</strong> — a named set of surface elements.</span>

          <span class="inline-flex items-center justify-center size-5 text-ui-text-secondary">
            <EdgeIcon class="size-3.5" />
          </span>
          <span><strong>Edge group</strong> — a named set of 1D line elements.</span>

          <span class="inline-flex items-center justify-center size-5 text-ui-text-secondary">
            <NodeIcon class="size-3.5" />
          </span>
          <span><strong>Node group</strong> — a named set of discrete points.</span>

          <span class="col-span-2 h-px bg-ui-border my-1"></span>

          <span
            class="relative inline-flex items-center text-[0.65rem] px-2 pt-0.5 pb-1 rounded-sm bg-ui-elem-hover text-ui-fg font-semibold min-w-16"
          >
            <span class="absolute left-1 top-0.5"><FaceIcon class="size-3.5" /></span>
            <span class="pl-4">group_A</span>
          </span>
          <span
            >Click a group to <strong>highlight</strong> it — the object becomes transparent so the group
            stands out. Click again to unhighlight.</span
          >

          <span
            class="w-fit inline-flex flex-col items-center rounded-sm overflow-hidden bg-ui-muted border border-ui-border"
          >
            <span class="size-5 flex items-center justify-center bg-ui-elem-hover text-ui-fg"
              ><FilterIcon class="size-3" /></span
            >
            <span class="w-3/4 h-px bg-ui-border"></span>
            <span class="size-5 flex items-center justify-center text-ui-text-muted"
              ><ClearIcon class="size-3" /></span
            >
          </span>
          <span
            >Click to <strong>choose which groups appear</strong> in the sidebar — hidden groups remain
            visible in the 3D view</span
          >

          <span
            class="w-fit inline-flex flex-col items-center rounded-sm overflow-hidden bg-ui-muted border border-ui-border"
          >
            <span class="size-5 flex items-center justify-center text-ui-text-muted"
              ><FilterIcon class="size-3" /></span
            >
            <span class="w-3/4 h-px bg-ui-border"></span>
            <span class="size-5 flex items-center justify-center bg-ui-elem-hover text-ui-fg"
              ><ClearIcon class="size-3" /></span
            >
          </span>
          <span>Click to <strong>clear all highlights</strong></span>
        </div>
      {:else if activeTab === 'Files'}
        <div class="space-y-2 text-ui-text-secondary">
          <p>
            <code>.med</code> mesh files are automatically converted to <code>.obj</code> when opened.
          </p>
          <p>
            Extension-generated files live in a hidden <code>.vs-code-aster/</code> folder next to
            your project:
            <code>mesh_cache/</code> for converted meshes,
            <code>screenshots/</code> for viewer captures,
            <code>run_logs/</code> for code_aster run output.
          </p>
        </div>
      {:else if activeTab === 'About'}
        <div class="space-y-3 text-ui-text-secondary">
          <p>
            This extension is made by <a
              href="https://simvia.tech"
              target="_blank"
              rel="noopener noreferrer"
              class="text-ui-link underline">Simvia</a
            >.
          </p>
          <p>
            Source code and issue tracker are available on <a
              href="https://github.com/simvia-tech/vs-code-aster"
              target="_blank"
              rel="noopener noreferrer"
              class="text-ui-link underline">GitHub</a
            >.
          </p>
        </div>
      {/if}
    </div>

    <div class="mt-4 flex justify-end">
      <button
        class="font-bold px-3 py-1 rounded-sm cursor-pointer text-xs bg-ui-btn hover:bg-ui-btn-hover text-ui-btn-fg"
        onclick={onclose}
      >
        Close
      </button>
    </div>
  </div>
</div>

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
