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
  <rect x="2" y="6" width="20" height="14" rx="2" />
  <circle cx="12" cy="13" r="4" />
  <path d="M9 6L10 3h4l1 3" />
</svg>
