<script lang="ts">
  import { tick } from 'svelte';
  import { toBlob as domToBlob } from 'html-to-image';
  import { VtkApp } from '../../lib/core/VtkApp';
  import { Controller } from '../../lib/Controller';
  import ScreenshotIcon from '../../icons/ScreenshotIcon.svelte';

  let tooltipFile = $state<string | null>(null);
  let tooltipClip = $state<string | null>(null);
  let visible = $state(false);
  let flash = $state(false);
  let capturing = $state(false);
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

  async function canvasOnlyBlob(): Promise<Blob | null> {
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

  async function onContextMenu(e: MouseEvent) {
    e.preventDefault();
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

  let showHoverTip = $derived(!tooltipFile);
</script>

<button
  class="group relative size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {capturing
    ? 'text-ui-text-secondary bg-transparent!'
    : flash
      ? 'bg-ui-elem text-ui-link transition-colors'
      : 'text-ui-text-secondary hover:bg-ui-elem transition-colors'}"
  onclick={onClick}
  oncontextmenu={onContextMenu}
>
  <ScreenshotIcon class="size-3.5" />
  {#if showHoverTip && !capturing}
    <span
      class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 hidden group-hover:inline whitespace-nowrap text-ui-text-secondary text-xs"
    >
      Screenshot
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
