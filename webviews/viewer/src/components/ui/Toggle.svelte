<script lang="ts">
  interface Props {
    checked: boolean;
    onclick: () => void;
    ariaLabel: string;
    size?: 'sm' | 'md';
  }

  let { checked, onclick, ariaLabel, size = 'md' }: Props = $props();

  const sizes = {
    md: {
      button: 'h-5 w-9',
      thumb: 'h-3.5 w-3.5',
      translateOn: 'translateX(19px)',
      translateOff: 'translateX(3px)',
    },
    sm: {
      button: 'h-3 w-6',
      thumb: 'h-1.5 w-1.5',
      translateOn: 'translateX(15px)',
      translateOff: 'translateX(3px)',
    },
  };

  const s = $derived(sizes[size]);
</script>

<button
  role="switch"
  aria-label={ariaLabel}
  aria-checked={checked}
  class="relative inline-flex {s.button} shrink-0 rounded-full transition-colors duration-150 focus:outline-none cursor-pointer {checked
    ? 'bg-ui-link'
    : 'bg-ui-border'}"
  {onclick}
>
  <span
    class="inline-block {s.thumb} rounded-full bg-white shadow-sm transition-transform duration-150 mt-0.75"
    style={checked ? `transform: ${s.translateOn}` : `transform: ${s.translateOff}`}
  ></span>
</button>
