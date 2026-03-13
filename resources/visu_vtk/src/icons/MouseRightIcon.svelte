<script lang="ts">
  let { class: className = '' } = $props();
</script>

<svg
  class={className}
  viewBox="0 0 24 24"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <path
    d="M 12,2 L 13,2 A 5,5 0 0,1 18,7 L 18,12 L 12,12 Z"
    stroke="none"
    class="fill-ui-link"
  />
  <rect x="6" y="2" width="12" height="20" rx="5" />
  <line x1="6" y1="12" x2="18" y2="12" />
  <line x1="12" y1="2" x2="12" y2="12" />
  <rect x="10.5" y="4" width="3" height="5" rx="1.5" stroke-width="1.5" />
</svg>
