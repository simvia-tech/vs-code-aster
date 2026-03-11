<script lang="ts">
  import { CameraManager } from '../lib/interaction/CameraManager';
</script>

<div class="flex justify-center space-x-1.5">
  <button
    title="Rotate camera to x-axis"
    class="flex items-center justify-center size-5.5 p-1 text-[0.65rem] font-bold text-red-500 border-2 border-red-500 rounded-full cursor-pointer hover:text-white hover:bg-red-500"
    onclick={() => CameraManager.Instance.setCameraAxis('x')}
  >
    X
  </button>
  <button
    title="Rotate camera to y-axis"
    class="flex items-center justify-center size-5.5 p-1 text-[0.65rem] font-bold text-green-500 border-2 border-green-500 rounded-full cursor-pointer hover:text-white hover:bg-green-500"
    onclick={() => CameraManager.Instance.setCameraAxis('y')}
  >
    Y
  </button>
  <button
    title="Rotate camera to z-axis"
    class="flex items-center justify-center size-5.5 p-1 text-[0.65rem] font-bold text-blue-500 border-2 border-blue-500 rounded-full cursor-pointer hover:text-white hover:bg-blue-500"
    onclick={() => CameraManager.Instance.setCameraAxis('z')}
  >
    Z
  </button>
</div>
