<script lang="ts">
  import { CameraManager } from '../../lib/interaction/CameraManager';
</script>

<div class="flex justify-center space-x-1">
  <button
    title="Rotate camera to x-axis"
    class="flex items-center justify-center size-6 text-[0.75rem] font-bold text-red-500 cursor-pointer hover:bg-red-500/15 rounded-sm"
    onclick={() => CameraManager.Instance.setCameraAxis('x')}
  >
    X
  </button>
  <button
    title="Rotate camera to y-axis"
    class="flex items-center justify-center size-6 text-[0.75rem] font-bold text-green-500 cursor-pointer hover:bg-green-500/15 rounded-sm"
    onclick={() => CameraManager.Instance.setCameraAxis('y')}
  >
    Y
  </button>
  <button
    title="Rotate camera to z-axis"
    class="flex items-center justify-center size-6 text-[0.75rem] font-bold text-blue-500 cursor-pointer hover:bg-blue-500/15 rounded-sm"
    onclick={() => CameraManager.Instance.setCameraAxis('z')}
  >
    Z
  </button>
</div>
