<script lang="ts">
  import { toBlob as domToBlob } from 'html-to-image';
  import { VtkApp } from '../../lib/core/VtkApp';
  import { Controller } from '../../lib/Controller';
  import ScreenshotIcon from '../../icons/ScreenshotIcon.svelte';

  let tooltipFile = $state<string | null>(null);
  let tooltipClip = $state<string | null>(null);
  let visible = $state(false);
  let flash = $state(false);
  let hideTimer: ReturnType<typeof setTimeout> | null = null;

  function getVtkCanvas(): HTMLCanvasElement | null {
    return document.querySelector('#scene canvas') as HTMLCanvasElement | null;
  }

  function canvasOnlyBlob(): Promise<Blob | null> {
    VtkApp.Instance.getRenderWindow().render();
    const canvas = getVtkCanvas();
    if (!canvas) return Promise.resolve(null);
    return new Promise((r) => canvas.toBlob(r, 'image/png'));
  }

  async function fullWebviewBlob(): Promise<Blob | null> {
    VtkApp.Instance.getRenderWindow().render();
    const vtkCanvas = getVtkCanvas();
    const dpr = window.devicePixelRatio || 1;
    const w = document.body.offsetWidth;
    const h = document.body.offsetHeight;

    const composite = document.createElement('canvas');
    composite.width = w * dpr;
    composite.height = h * dpr;
    const ctx = composite.getContext('2d');
    if (!ctx) return null;
    ctx.scale(dpr, dpr);

    if (vtkCanvas) {
      ctx.drawImage(vtkCanvas, 0, 0, w, h);
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
    await send(await fullWebviewBlob());
  }

  let showHoverTip = $derived(!tooltipFile);
</script>

<button
  class="group relative size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] transition-colors {flash
    ? 'bg-ui-elem text-ui-link'
    : 'text-ui-text-secondary hover:bg-ui-elem'}"
  onclick={onClick}
  oncontextmenu={onContextMenu}
>
  <ScreenshotIcon class="size-3.5" />
  {#if showHoverTip}
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
