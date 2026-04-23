<script lang="ts">
  import { toBlob as domToBlob } from 'html-to-image';
  import { Controller } from '../../lib/Controller';
  import { VtkApp } from '../../lib/core/VtkApp';
  import { openToolbarPopover } from '../../lib/state';
  import RecordIcon from '../../icons/RecordIcon.svelte';

  const POPOVER_ID = 'record';
  const FPS = 60;
  const BITRATE = 12_000_000;
  const OVERLAY_PIXEL_RATIO = 1;
  const SIDEBAR_THROTTLE_MS = 1000;

  let recording = $state(false);
  let mediaRecorder: MediaRecorder | null = null;
  let chunks: Blob[] = [];
  let rafHandle: number | null = null;
  let composite: HTMLCanvasElement | null = null;
  let vtkSnapshot: HTMLCanvasElement | null = null;
  let vtkSnapshotCtx: CanvasRenderingContext2D | null = null;
  let vtkRenderSub: { unsubscribe(): void } | null = null;
  let activeStream: MediaStream | null = null;
  let mimeType = '';

  let tooltipMsg = $state<string | null>(null);
  let tooltipVisible = $state(false);
  let hideTimer: ReturnType<typeof setTimeout> | null = null;
  let elapsed = $state(0);
  let startedAt = 0;
  let elapsedTimer: ReturnType<typeof setInterval> | null = null;

  let popoverOpen = $derived($openToolbarPopover === POPOVER_ID);
  let wrapper: HTMLDivElement | undefined = $state();

  /**
   * Bounds of the visible viewport excluding the sidebar. Used to crop canvas
   * captures when the sidebar isn't baked into the recording, so the mesh
   * (which is camera-offset to stay centered in this region) doesn't end up
   * off-center in the output.
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

  function getVtkCanvas(): HTMLCanvasElement | null {
    const canvases = Array.from(document.querySelectorAll('#scene canvas'));
    for (const c of canvases) {
      if (!c.classList.contains('dream-canvas')) return c as HTMLCanvasElement;
    }
    return null;
  }

  function getDreamCanvas(): HTMLCanvasElement | null {
    return document.querySelector('#scene canvas.dream-canvas') as HTMLCanvasElement | null;
  }

  function pickMimeType(): string {
    const candidates = [
      'video/mp4;codecs=avc1.42E01E',
      'video/mp4;codecs=h264',
      'video/mp4',
      'video/webm;codecs=vp9',
      'video/webm;codecs=vp8',
      'video/webm',
    ];
    for (const t of candidates) {
      if (MediaRecorder.isTypeSupported(t)) return t;
    }
    return '';
  }

  function extForMime(mt: string): string {
    return mt.startsWith('video/mp4') ? 'mp4' : 'webm';
  }

  /**
   * Subscribe to VTK's post-render event and copy the live canvas into a 2D
   * snapshot canvas there — the only moment the WebGL drawing buffer is
   * guaranteed to hold a complete frame. Compositor RAF samples from this
   * snapshot instead of the live canvas, avoiding blink during mouse-drag
   * where VTK is mid-render when our RAF fires.
   */
  function setupVtkSnapshot(vtk: HTMLCanvasElement) {
    // Force a fresh render so the WebGL buffer is guaranteed to hold a
    // complete frame before we prime the snapshot — otherwise the first
    // video frames can be blank until the user interacts with the view.
    VtkApp.Instance.getRenderWindow().render();
    vtkSnapshot = document.createElement('canvas');
    vtkSnapshot.width = vtk.width;
    vtkSnapshot.height = vtk.height;
    vtkSnapshotCtx = vtkSnapshot.getContext('2d');
    vtkSnapshotCtx?.drawImage(vtk, 0, 0);
    const interactor = VtkApp.Instance.getRenderWindow().getInteractor();
    vtkRenderSub = interactor.onRenderEvent(() => {
      if (!vtkSnapshot || !vtkSnapshotCtx) return;
      if (vtkSnapshot.width !== vtk.width || vtkSnapshot.height !== vtk.height) {
        vtkSnapshot.width = vtk.width;
        vtkSnapshot.height = vtk.height;
      }
      // Clear before drawImage: the VTK canvas has alpha:true, so
      // background pixels are transparent and without clearing, successive
      // frames accumulate on the snapshot producing a ghost/trail effect.
      vtkSnapshotCtx.clearRect(0, 0, vtkSnapshot.width, vtkSnapshot.height);
      vtkSnapshotCtx.drawImage(vtk, 0, 0);
    });
  }

  function teardownVtkSnapshot() {
    vtkRenderSub?.unsubscribe();
    vtkRenderSub = null;
    vtkSnapshot = null;
    vtkSnapshotCtx = null;
  }

  async function startCanvasRecording() {
    const vtk = getVtkCanvas();
    if (!vtk) {
      showToast('No viewport to record');
      return;
    }
    mimeType = pickMimeType();
    if (!mimeType) {
      showToast('Recording not supported');
      return;
    }

    const dpr = window.devicePixelRatio || 1;
    const bounds = getContentBounds();
    const cw = Math.round(bounds.w * dpr);
    const ch = Math.round(bounds.h * dpr);
    composite = document.createElement('canvas');
    composite.width = cw;
    composite.height = ch;
    const ctx = composite.getContext('2d');
    if (!ctx) return;

    setupVtkSnapshot(vtk);

    const vtkRect = vtk.getBoundingClientRect();

    const draw = () => {
      ctx.clearRect(0, 0, cw, ch);
      const dream = getDreamCanvas();
      if (dream) {
        const dRect = dream.getBoundingClientRect();
        // Source rect on the dream canvas covering the content-bounds region,
        // in device pixels.
        const sx = (bounds.x - dRect.left) * dpr;
        const sy = (bounds.y - dRect.top) * dpr;
        const sw = bounds.w * dpr;
        const sh = bounds.h * dpr;
        try {
          ctx.drawImage(dream, sx, sy, sw, sh, 0, 0, cw, ch);
        } catch {
          /* ignore cross-surface issues */
        }
      }
      if (vtkSnapshot) {
        const sx = (bounds.x - vtkRect.left) * dpr;
        const sy = (bounds.y - vtkRect.top) * dpr;
        const sw = bounds.w * dpr;
        const sh = bounds.h * dpr;
        ctx.drawImage(vtkSnapshot, sx, sy, sw, sh, 0, 0, cw, ch);
      }
      rafHandle = requestAnimationFrame(draw);
    };
    rafHandle = requestAnimationFrame(draw);

    const stream = (
      composite as HTMLCanvasElement & {
        captureStream(fps?: number): MediaStream;
      }
    ).captureStream(FPS);
    activeStream = stream;
    beginRecorder(stream);
  }

  // Overlay is split into two independently-refreshed layers so a toolbar
  // click doesn't pay the sidebar rasterization cost and vice-versa. The
  // observer classifies each mutation into either shell (`#controls` OFF)
  // or sidebar (`#controls` ON), and only the dirty layer is rerastered.
  let shellImg: HTMLImageElement | null = null;
  let sidebarImg: HTMLImageElement | null = null;
  let shellInFlight = false;
  let sidebarInFlight = false;
  let shellDirty = false;
  let sidebarDirty = false;
  let overlayObserver: MutationObserver | null = null;
  let overlayIncludeSidebar = true;
  let sidebarLastRasterAt = 0;
  let sidebarTrailingTimer: ReturnType<typeof setTimeout> | null = null;

  function flushOverlayRefresh() {
    if (shellDirty) {
      shellDirty = false;
      void refreshShell();
    }
    if (sidebarDirty && overlayIncludeSidebar) {
      // Throttle sidebar raster (expensive) to at most one per
      // SIDEBAR_THROTTLE_MS, with a leading edge (raster immediately if
      // enough time has passed) and a trailing edge (queue a final raster
      // to capture the end state of a rapid interaction burst).
      const now = performance.now();
      const delta = now - sidebarLastRasterAt;
      if (delta >= SIDEBAR_THROTTLE_MS) {
        sidebarDirty = false;
        sidebarLastRasterAt = now;
        void refreshSidebar();
      } else if (sidebarTrailingTimer === null) {
        sidebarTrailingTimer = setTimeout(() => {
          sidebarTrailingTimer = null;
          if (sidebarDirty && overlayIncludeSidebar) {
            sidebarDirty = false;
            sidebarLastRasterAt = performance.now();
            void refreshSidebar();
          }
        }, SIDEBAR_THROTTLE_MS - delta);
      }
    }
  }

  function classifyMutation(r: MutationRecord): 'shell' | 'sidebar' | 'ignore' {
    const target = r.target as Element | null;
    if (!target) return 'ignore';
    if (wrapper && wrapper.contains(target)) return 'ignore';
    const el =
      target.nodeType === Node.ELEMENT_NODE
        ? (target as HTMLElement)
        : ((target.parentElement as HTMLElement) ?? null);
    if (!el) return 'ignore';
    const id = el.id || '';
    if (id === 'zoomIndicator' || id === 'zoomWidget') return 'ignore';
    if (id.startsWith('bboxLabel')) return 'ignore';
    if (el.closest && (el.closest('#zoomWidget') || el.closest('[id^="bboxLabel"]'))) {
      return 'ignore';
    }
    if (el.closest && el.closest('#controls')) return 'sidebar';
    return 'shell';
  }

  function onDomMutation(records: MutationRecord[]) {
    let scheduled = false;
    for (const r of records) {
      const kind = classifyMutation(r);
      if (kind === 'ignore') continue;
      if (kind === 'shell') shellDirty = true;
      else sidebarDirty = true;
      scheduled = true;
    }
    if (scheduled) flushOverlayRefresh();
  }

  async function blobToImage(blob: Blob): Promise<HTMLImageElement> {
    const img = new Image();
    img.src = URL.createObjectURL(blob);
    await new Promise<void>((r, rej) => {
      img.onload = () => r();
      img.onerror = () => rej();
    });
    return img;
  }

  async function refreshShell() {
    if (shellInFlight) {
      shellDirty = true;
      return;
    }
    shellInFlight = true;
    try {
      const blob = await domToBlob(document.body, {
        pixelRatio: OVERLAY_PIXEL_RATIO,
        cacheBust: false,
        filter: (node: Node) => {
          if (node instanceof HTMLCanvasElement) return false;
          const el = node as HTMLElement;
          if (el.id === 'scene') return false;
          if (el.id === 'controls') return false;
          return true;
        },
      });
      if (!blob) return;
      const img = await blobToImage(blob);
      if (shellImg) URL.revokeObjectURL(shellImg.src);
      shellImg = img;
    } catch {
      /* ignore transient rasterization failures */
    } finally {
      shellInFlight = false;
    }
  }

  async function refreshSidebar() {
    if (!overlayIncludeSidebar) return;
    if (sidebarInFlight) {
      sidebarDirty = true;
      return;
    }
    const sidebar = document.getElementById('controls');
    if (!sidebar) return;
    sidebarInFlight = true;
    try {
      const blob = await domToBlob(sidebar, {
        pixelRatio: OVERLAY_PIXEL_RATIO,
        cacheBust: false,
      });
      if (!blob) return;
      const img = await blobToImage(blob);
      if (sidebarImg) URL.revokeObjectURL(sidebarImg.src);
      sidebarImg = img;
    } catch {
      /* ignore transient rasterization failures */
    } finally {
      sidebarInFlight = false;
    }
  }

  async function startWebviewRecording(excludeSidebar = false) {
    const vtk = getVtkCanvas();
    if (!vtk) {
      showToast('No viewport to record');
      return;
    }
    mimeType = pickMimeType();
    if (!mimeType) {
      showToast('Recording not supported');
      return;
    }

    const dpr = window.devicePixelRatio || 1;
    // Without-sidebar recordings crop to the content region so the mesh
    // (which is camera-offset to stay centered in this region) is centered
    // in the output. Whole-webview recordings keep the full viewport since
    // the sidebar is baked into the frame.
    const bounds = excludeSidebar
      ? getContentBounds()
      : {
          x: 0,
          y: 0,
          w: document.body.offsetWidth,
          h: document.body.offsetHeight,
          vw: document.body.offsetWidth,
          vh: document.body.offsetHeight,
        };
    const w = Math.round(bounds.w * dpr);
    const h = Math.round(bounds.h * dpr);
    composite = document.createElement('canvas');
    composite.width = w;
    composite.height = h;
    const ctx = composite.getContext('2d');
    if (!ctx) return;

    overlayIncludeSidebar = !excludeSidebar;
    await refreshShell();
    if (overlayIncludeSidebar) await refreshSidebar();
    overlayObserver = new MutationObserver(onDomMutation);
    overlayObserver.observe(document.body, {
      subtree: true,
      childList: true,
      attributes: true,
      characterData: true,
    });

    setupVtkSnapshot(vtk);

    const sidebarEl = document.getElementById('controls');

    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      const dream = getDreamCanvas();
      if (dream) {
        const dRect = dream.getBoundingClientRect();
        const sx = (bounds.x - dRect.left) * dpr;
        const sy = (bounds.y - dRect.top) * dpr;
        ctx.drawImage(dream, sx, sy, bounds.w * dpr, bounds.h * dpr, 0, 0, w, h);
      }
      const rect = vtk.getBoundingClientRect();
      if (vtkSnapshot) {
        // Draw vtkSnapshot at its on-screen position, translated by -bounds.x/y.
        ctx.drawImage(
          vtkSnapshot,
          Math.round((rect.left - bounds.x) * dpr),
          Math.round((rect.top - bounds.y) * dpr),
          Math.round(rect.width * dpr),
          Math.round(rect.height * dpr)
        );
      }
      // Sidebar layer sits below shell so popups/toolbar visually cover it.
      if (sidebarImg && overlayIncludeSidebar && sidebarEl) {
        const sRect = sidebarEl.getBoundingClientRect();
        ctx.drawImage(
          sidebarImg,
          Math.round((sRect.left - bounds.x) * dpr),
          Math.round((sRect.top - bounds.y) * dpr),
          Math.round(sRect.width * dpr),
          Math.round(sRect.height * dpr)
        );
      }
      if (shellImg) {
        // Shell overlay is rasterized at OVERLAY_PIXEL_RATIO (not dpr),
        // so source coordinates must be in OVERLAY_PIXEL_RATIO-scaled units.
        ctx.drawImage(
          shellImg,
          bounds.x * OVERLAY_PIXEL_RATIO,
          bounds.y * OVERLAY_PIXEL_RATIO,
          bounds.w * OVERLAY_PIXEL_RATIO,
          bounds.h * OVERLAY_PIXEL_RATIO,
          0,
          0,
          w,
          h
        );
      }
      rafHandle = requestAnimationFrame(draw);
    };
    rafHandle = requestAnimationFrame(draw);

    const stream = (
      composite as HTMLCanvasElement & {
        captureStream(fps?: number): MediaStream;
      }
    ).captureStream(FPS);
    activeStream = stream;
    beginRecorder(stream);
  }

  function beginRecorder(stream: MediaStream) {
    chunks = [];
    mediaRecorder = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: BITRATE,
    });
    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunks.push(e.data);
    };
    mediaRecorder.onstop = async () => {
      if (rafHandle !== null) cancelAnimationFrame(rafHandle);
      rafHandle = null;
      if (elapsedTimer) clearInterval(elapsedTimer);
      elapsedTimer = null;
      teardownVtkSnapshot();
      if (overlayObserver) {
        overlayObserver.disconnect();
        overlayObserver = null;
      }
      if (sidebarTrailingTimer !== null) {
        clearTimeout(sidebarTrailingTimer);
        sidebarTrailingTimer = null;
      }
      sidebarLastRasterAt = 0;
      overlayIncludeSidebar = true;
      shellDirty = false;
      sidebarDirty = false;
      if (shellImg) {
        URL.revokeObjectURL(shellImg.src);
        shellImg = null;
      }
      if (sidebarImg) {
        URL.revokeObjectURL(sidebarImg.src);
        sidebarImg = null;
      }
      activeStream?.getTracks().forEach((t) => t.stop());
      activeStream = null;
      const blob = new Blob(chunks, { type: mimeType });
      await saveBlob(blob);
      chunks = [];
      composite = null;
    };
    mediaRecorder.start();
    startedAt = performance.now();
    elapsed = 0;
    elapsedTimer = setInterval(() => {
      elapsed = Math.floor((performance.now() - startedAt) / 1000);
    }, 500);
    recording = true;
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    recording = false;
  }

  async function saveBlob(blob: Blob) {
    const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const ext = extForMime(mimeType);
    const filename = `recording-${stamp}.${ext}`;
    const reader = new FileReader();
    reader.onload = () => {
      Controller.Instance.getVSCodeAPI().postMessage({
        type: 'saveRecording',
        dataUrl: reader.result,
        filename,
      });
    };
    reader.readAsDataURL(blob);
    showToast(`Saved as ${filename}`);
  }

  function showToast(msg: string) {
    tooltipMsg = msg;
    if (hideTimer) clearTimeout(hideTimer);
    requestAnimationFrame(() => (tooltipVisible = true));
    hideTimer = setTimeout(() => {
      tooltipVisible = false;
      setTimeout(() => (tooltipMsg = null), 200);
    }, 3000);
  }

  function onClick() {
    if (recording) stopRecording();
    else startCanvasRecording();
  }

  async function recordWholeWebview() {
    openToolbarPopover.set(null);
    await startWebviewRecording(false);
  }

  async function recordWithoutSidebar() {
    openToolbarPopover.set(null);
    await startWebviewRecording(true);
  }

  function onContextMenu(e: MouseEvent) {
    e.preventDefault();
    if (recording) return;
    openToolbarPopover.set(popoverOpen ? null : POPOVER_ID);
  }

  function onDocClick(e: MouseEvent) {
    if (!popoverOpen) return;
    if (wrapper && !wrapper.contains(e.target as Node)) {
      openToolbarPopover.set(null);
    }
  }

  function formatElapsed(s: number): string {
    const m = Math.floor(s / 60);
    const r = s % 60;
    return `${m}:${r.toString().padStart(2, '0')}`;
  }
</script>

<svelte:document onclick={onDocClick} />

<div bind:this={wrapper} class="relative flex items-stretch">
  <button
    class="group relative size-6 p-1 flex items-center justify-center cursor-pointer stroke-[1.75] {recording
      ? 'bg-red-500/20 text-red-500'
      : popoverOpen
        ? 'bg-ui-elem text-ui-link'
        : 'text-ui-text-secondary hover:bg-ui-elem'}"
    onclick={onClick}
    oncontextmenu={onContextMenu}
  >
    <RecordIcon class="size-3.5" />
    {#if recording}
      <span
        class="absolute -top-1 -right-1 size-1.5 rounded-full bg-red-500 animate-pulse"
        aria-hidden="true"
      ></span>
      <span
        class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 whitespace-nowrap text-red-500 text-xs font-mono"
      >
        ● {formatElapsed(elapsed)}
      </span>
    {:else if !tooltipMsg && !popoverOpen}
      <span
        class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 hidden group-hover:inline whitespace-nowrap text-ui-text-secondary text-xs"
      >
        Record (right-click for options)
      </span>
    {/if}
    {#if tooltipMsg && !recording}
      <div
        class="absolute top-full left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full px-3 py-1.5 text-xs text-center bg-ui-muted text-ui-text-secondary pointer-events-none transition-all duration-200 ease-out {tooltipVisible
          ? 'opacity-100 mt-2'
          : 'opacity-0 mt-0'}"
      >
        {tooltipMsg}
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
        onclick={recordWholeWebview}
      >
        Record whole webview
      </button>
      <button
        class="w-full text-left text-xs px-2 py-1.5 rounded-sm cursor-pointer hover:bg-ui-elem text-ui-fg"
        onclick={recordWithoutSidebar}
      >
        Record without sidebar
      </button>
    </div>
  {/if}
</div>
