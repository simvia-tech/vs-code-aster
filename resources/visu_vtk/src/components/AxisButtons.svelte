<script lang="ts">
  import { CameraManager } from '../lib/interaction/CameraManager';
</script>

<div class="flex justify-center space-x-1.5">
  <button
    title="Rotate camera to x-axis"
    class="flex items-center justify-center size-5.5 p-1 text-[0.65rem] font-bold text-red-500 border-2 border-red-500 rounded-full cursor-pointer hover:text-white"
    onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgb(239,68,68)'; }}
    onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
    onclick={() => CameraManager.Instance.setCameraAxis('x')}
  >
    X
  </button>
  <button
    title="Rotate camera to y-axis"
    class="flex items-center justify-center size-5.5 p-1 text-[0.65rem] font-bold text-green-500 border-2 border-green-500 rounded-full cursor-pointer hover:text-white"
    onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgb(34,197,94)'; }}
    onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
    onclick={() => CameraManager.Instance.setCameraAxis('y')}
  >
    Y
  </button>
  <button
    title="Rotate camera to z-axis"
    class="flex items-center justify-center size-5.5 p-1 text-[0.65rem] font-bold text-blue-500 border-2 border-blue-500 rounded-full cursor-pointer hover:text-white"
    onmouseover={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgb(59,130,246)'; }}
    onmouseout={(e) => { (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
    onclick={() => CameraManager.Instance.setCameraAxis('z')}
  >
    Z
  </button>
</div>
