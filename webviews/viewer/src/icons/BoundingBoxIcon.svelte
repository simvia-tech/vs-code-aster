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
  <rect x="4" y="8" width="12" height="12" />
  <rect x="8" y="4" width="12" height="12" />
  <path d="M4 8L8 4" />
  <path d="M16 8L20 4" />
  <path d="M16 20L20 16" />
  <path d="M4 20L8 16" />
</svg>
