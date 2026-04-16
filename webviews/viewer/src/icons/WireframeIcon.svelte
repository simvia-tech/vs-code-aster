<script lang="ts">
  let { class: className = '' } = $props();
</script>

<svg
  class={className}
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <path d="M4 19L12 5L20 19Z" />
  <line x1="8" y1="12" x2="16" y2="12" />
  <line x1="8" y1="12" x2="12" y2="19" />
  <line x1="16" y1="12" x2="12" y2="19" />
</svg>
