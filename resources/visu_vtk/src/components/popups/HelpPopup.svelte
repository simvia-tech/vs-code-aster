<script lang="ts">
  import ClearIcon from '../../icons/ClearIcon.svelte';
  import FilterIcon from '../../icons/FilterIcon.svelte';

  let { onclose }: { onclose: () => void } = $props();
</script>

<div
  id="helpPopup"
  class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-2/3 max-h-2/3 rounded shadow-lg backdrop-blur-lg p-8 flex flex-col"
  style="background: var(--ui-popup-bg); color: var(--ui-fg); border: 1px solid var(--ui-border)"
  role="document"
>
  <span class="font-bold text-base">Help</span>

  <div class="flex flex-col space-y-4 mt-4 pr-2 overflow-y-auto grow">
    <div class="flex flex-col space-y-1 mb-4">
      <span class="font-bold">Group highlighting</span>
      <ul class="text-xs space-y-1 list-disc list-inside">
        <li>Click on a group name in the sidebar to highlight or unhighlight it</li>
        <li>
          Click on the
          <span class="inline-flex align-top"><ClearIcon class="size-4" /></span>
          button in the sidebar to reset highlight status for all groups
        </li>
        <li>
          Click on the
          <span class="inline-flex align-top"><FilterIcon class="size-4" /></span>
          button in the sidebar to choose which groups are easily accessible in the sidebar
        </li>
        <li>Objects becomes transparent when you highlight their groups, helping visualize details more clearly</li>
      </ul>
    </div>

    <div class="flex flex-col space-y-1 mb-4">
      <span class="font-bold">Camera control</span>
      <ul class="text-xs space-y-1 list-disc list-inside">
        <li>Hold <kbd>Left click</kbd> and move your mouse to rotate the camera</li>
        <li>Hold <kbd>Ctrl</kbd> + <kbd>Left click</kbd> and move your mouse to rotate the camera around an axis</li>
        <li>Hold <kbd>Shift</kbd> + <kbd>Left click</kbd> and move your mouse to pan the camera</li>
        <li>Use the <kbd>Mouse wheel</kbd> to zoom in and out</li>
        <li>
          Click on the <kbd class="text-red-600! font-bold">X</kbd>,
          <kbd class="text-green-600! font-bold">Y</kbd> and
          <kbd class="text-blue-500! font-bold">Z</kbd> buttons at the bottom of the sidebar to quickly align the camera along an axis
        </li>
      </ul>
    </div>

    <div class="flex flex-col space-y-1 mb-4">
      <span class="font-bold">File management</span>
      <ul class="text-xs space-y-1 list-disc list-inside">
        <li>
          Mesh files (<code>.*med</code> files) are converted to <code>.obj</code> files,
          which are stored in a hidden folder called <code>.visu_data/</code> in your workspace
        </li>
      </ul>
    </div>
  </div>

  <div class="mt-4 flex self-end space-x-3">
    <button
      class="font-bold px-3 py-1 rounded-sm cursor-pointer text-xs bg-ui-btn hover:bg-ui-btn-hover"
      style="color: var(--ui-btn-fg)"
      onclick={onclose}
    >
      Close
    </button>
  </div>
</div>
