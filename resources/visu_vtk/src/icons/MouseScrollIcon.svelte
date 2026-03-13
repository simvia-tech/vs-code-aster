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
  <rect x="6" y="2" width="12" height="20" rx="5" />
  <line x1="6" y1="12" x2="18" y2="12" />
  <line x1="12" y1="2" x2="12" y2="12" />
  <rect
    x="10.5"
    y="4"
    width="3"
    height="5"
    rx="1.5"
    style="fill: var(--vscode-textLink-foreground, #0078d4)"
    stroke="none"
  />
</svg>
