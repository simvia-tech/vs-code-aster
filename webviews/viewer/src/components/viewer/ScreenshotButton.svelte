<script lang="ts">
  import { tick } from 'svelte';
  import { toBlob as domToBlob } from 'html-to-image';
  import { VtkApp } from '../../lib/core/VtkApp';
  import { Controller } from '../../lib/Controller';
  import ScreenshotIcon from '../../icons/ScreenshotIcon.svelte';
  import { openToolbarPopover } from '../../lib/state';

  const POPOVER_ID = 'screenshot';

  let tooltipFile = $state<string | null>(null);
  let tooltipClip = $state<string | null>(null);
  let visible = $state(false);
  let flash = $state(false);
  let capturing = $state(false);
  let popoverOpen = $derived($openToolbarPopover === POPOVER_ID);
  let wrapper: HTMLDivElement | undefined = $state();
  let hideTimer: ReturnType<typeof setTimeout> | null = null;

  function getDreamCanvas(): HTMLCanvasElement | null {
    return document.querySelector('#scene canvas.dream-canvas') as HTMLCanvasElement | null;
  }

  async function captureVtkImage(): Promise<HTMLImageElement | null> {
    // vtk.js's captureNextImage() arms the render window, sets up a framebuffer
    // capture, and resolves once the next render completes. This works even
    // when preserveDrawingBuffer is off, unlike canvas.toBlob().
    const apiRW = (VtkApp.Instance as any).fullScreenRenderer?.getApiSpecificRenderWindow?.();
    if (!apiRW || typeof apiRW.captureNextImage !== 'function') return null;
    const promise: Promise<string> = apiRW.captureNextImage('image/png');
    VtkApp.Instance.getRenderWindow().render();
    const dataUrl = await promise;
    if (!dataUrl) return null;
    const img = new Image();
    img.src = dataUrl;
    await new Promise<void>((r) => (img.onload = () => r()));
    return img;
  }

  /**
   * Bounds of the visible viewport excluding the sidebar. The mesh is camera-
   * offset by `updateCameraOffset` so it stays centered in this region; when
   * we capture without the sidebar overlay, we crop to this region so the
   * output is centered on the mesh rather than on the full window.
   */
  function getContentBounds() {
    const vw = document.body.offsetWidth;
    const vh = document.body.offsetHeight;
    const controls = document.getElementById('controls');
    if (!controls) return { x: 0, y: 0, w: vw, h: vh, vw, vh };
    const rect = controls.getBoundingClientRect();
    const sidebarOnLeft = rect.left < vw - rect.right;
    return {
      x: sidebarOnLeft ? rect.width : 0,
      y: 0,
      w: Math.max(0, vw - rect.width),
      h: vh,
      vw,
      vh,
    };
  }

  async function canvasOnlyBlob(): Promise<Blob | null> {
    const vtkImg = await captureVtkImage();
    const dream = getDreamCanvas();
    const dpr = window.devicePixelRatio || 1;
    const bounds = getContentBounds();

    const composite = document.createElement('canvas');
    composite.width = bounds.w * dpr;
    composite.height = bounds.h * dpr;
    const ctx = composite.getContext('2d');
    if (!ctx) return null;
    ctx.scale(dpr, dpr);

    if (dream) {
      ctx.drawImage(dream, -bounds.x, -bounds.y, bounds.vw, bounds.vh);
    }
    if (vtkImg) {
      ctx.drawImage(vtkImg, -bounds.x, -bounds.y, bounds.vw, bounds.vh);
    }

    return new Promise((r) => composite.toBlob(r, 'image/png'));
  }

  async function fullWebviewBlob(): Promise<Blob | null> {
    const vtkImg = await captureVtkImage();
    const dream = getDreamCanvas();
    const dpr = window.devicePixelRatio || 1;
    const w = document.body.offsetWidth;
    const h = document.body.offsetHeight;

    const composite = document.createElement('canvas');
    composite.width = w * dpr;
    composite.height = h * dpr;
    const ctx = composite.getContext('2d');
    if (!ctx) return null;
    ctx.scale(dpr, dpr);

    if (dream) {
      ctx.drawImage(dream, 0, 0, w, h);
    }
    if (vtkImg) {
      ctx.drawImage(vtkImg, 0, 0, w, h);
    }

    try {
      const overlay = await domToBlob(document.body, {
        pixelRatio: dpr,
        filter: (node: Node) =>
          !(node instanceof HTMLCanvasElement) && (node as HTMLElement).id !== 'scene',
      });
      if (overlay) {
        const img = new Image();
        img.src = URL.createObjectURL(overlay);
        await new Promise<void>((r) => (img.onload = () => r()));
        ctx.drawImage(img, 0, 0, w, h);
        URL.revokeObjectURL(img.src);
      }
    } catch {}

    return new Promise((r) => composite.toBlob(r, 'image/png'));
  }

  async function send(blob: Blob | null) {
    if (!blob) return;

    const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const filename = `screenshot-${stamp}.png`;

    const reader = new FileReader();
    reader.onload = () => {
      Controller.Instance.getVSCodeAPI().postMessage({
        type: 'saveScreenshot',
        dataUrl: reader.result,
        filename,
      });
    };
    reader.readAsDataURL(blob);

    try {
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
    } catch {}

    flash = true;
    tooltipFile = `Saved as ${filename}`;
    tooltipClip = 'Copied to clipboard';
    if (hideTimer) clearTimeout(hideTimer);
    requestAnimationFrame(() => (visible = true));
    setTimeout(() => (flash = false), 500);
    hideTimer = setTimeout(() => {
      visible = false;
      setTimeout(() => {
        tooltipFile = null;
        tooltipClip = null;
      }, 200);
    }, 3000);
  }

  async function onClick() {
    await send(await canvasOnlyBlob());
  }

  function onContextMenu(e: MouseEvent) {
    e.preventDefault();
    openToolbarPopover.set(popoverOpen ? null : POPOVER_ID);
  }

  async function captureFullWebview() {
    openToolbarPopover.set(null);
    // Strip hover styles from the button itself so the full-viewer capture
    // doesn't bake in the highlight produced by the right-click hover.
    capturing = true;
    await tick();
    try {
      await send(await fullWebviewBlob());
    } finally {
      capturing = false;
    }
  }

  function onDocClick(e: MouseEvent) {
    if (!popoverOpen) return;
    if (wrapper && !wrapper.contains(e.target as Node)) {
      openToolbarPopover.set(null);
    }
  }

  let showHoverTip = $derived(!tooltipFile && !popoverOpen);
</script>

<svelte:document onclick={onDocClick} />

<div bind:this={wrapper} class="relative flex items-stretch">
  <button
    class="group relative size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {capturing
      ? 'text-ui-text-secondary bg-transparent!'
      : flash
        ? 'bg-ui-elem text-ui-link transition-colors'
        : popoverOpen
          ? 'bg-ui-elem text-ui-link'
          : 'text-ui-text-secondary hover:bg-ui-elem transition-colors'}"
    onclick={onClick}
    oncontextmenu={onContextMenu}
  >
    <ScreenshotIcon class="size-3.5" />
    {#if showHoverTip && !capturing}
      <span
        class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 hidden group-hover:inline whitespace-nowrap text-ui-text-secondary text-xs"
      >
        Screenshot (right-click for options)
      </span>
    {/if}
    {#if tooltipFile}
      <div
        class="absolute top-full left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full px-3 py-1.5 text-xs text-center bg-ui-muted text-ui-text-secondary pointer-events-none transition-all duration-200 ease-out {visible
          ? 'opacity-100 mt-2'
          : 'opacity-0 mt-0'}"
      >
        <div>{tooltipFile}</div>
        <div>{tooltipClip}</div>
      </div>
    {/if}
  </button>

  {#if popoverOpen}
    <div
      class="absolute top-full left-0 mt-1 z-20 w-52 rounded shadow-lg border border-ui-border bg-ui-popup-bg p-1 text-ui-fg"
      role="menu"
    >
      <button
        class="w-full text-left text-xs px-2 py-1.5 rounded-sm cursor-pointer hover:bg-ui-elem text-ui-fg"
        onclick={captureFullWebview}
      >
        Screenshot whole screen
      </button>
    </div>
  {/if}
</div>
