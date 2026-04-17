<script lang="ts">
  interface Props {
    id: string;
    value: string;
    placeholder?: string;
    invalid?: boolean;
    suggestions: string[];
    onQuery: (value: string) => void;
    onFocusChange: (focused: boolean) => void;
  }

  let {
    id,
    value = $bindable(),
    placeholder = '',
    invalid = false,
    suggestions,
    onQuery,
    onFocusChange,
  }: Props = $props();

  let focused = $state(false);
  let selectedIndex = $state(0);
  let inputEl = $state<HTMLInputElement | null>(null);

  let showBox = $derived(focused && suggestions.length > 0);

  $effect(() => {
    if (suggestions.length === 0) selectedIndex = 0;
    else if (selectedIndex >= suggestions.length) selectedIndex = 0;
  });

  function handleInput() {
    onQuery(value);
  }

  function handleFocus() {
    focused = true;
    onFocusChange(true);
    onQuery(value);
  }

  function handleBlur() {
    // delay so clicking a suggestion can register
    setTimeout(() => {
      focused = false;
      onFocusChange(false);
    }, 100);
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (!showBox) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedIndex = (selectedIndex + 1) % suggestions.length;
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedIndex = (selectedIndex - 1 + suggestions.length) % suggestions.length;
    } else if (e.key === 'Enter' || e.key === 'Tab' || e.key === 'ArrowRight') {
      e.preventDefault();
      value = suggestions[selectedIndex];
      onQuery(value);
      focused = false;
      onFocusChange(false);
      inputEl?.blur();
    } else if (e.key === 'Escape') {
      focused = false;
      onFocusChange(false);
      inputEl?.blur();
    }
  }

  function pickSuggestion(i: number) {
    value = suggestions[i];
    onQuery(value);
    focused = false;
    onFocusChange(false);
  }
</script>

<div class="relative flex-1 min-w-0">
  <input
    bind:this={inputEl}
    {id}
    type="text"
    class="w-full bg-ui-popup-bg text-ui-fg border border-ui-border rounded px-2 py-1 text-sm focus:border-ui-btn focus:outline-none"
    class:input-warning={invalid}
    {placeholder}
    bind:value
    oninput={handleInput}
    onfocus={handleFocus}
    onblur={handleBlur}
    onkeydown={handleKeyDown}
  />
  {#if showBox}
    <ul
      class="absolute left-0 right-0 top-full mt-0.5 z-20 bg-ui-popup-bg border border-ui-border rounded shadow-md max-h-48 overflow-y-auto"
      role="listbox"
    >
      {#each suggestions as s, i}
        <li
          class="px-2 py-1 text-sm cursor-pointer text-ui-fg {i === selectedIndex
            ? 'bg-ui-elem-hover font-semibold'
            : 'hover:bg-ui-elem'}"
          role="option"
          aria-selected={i === selectedIndex}
          onmousedown={(e) => {
            e.preventDefault();
            pickSuggestion(i);
          }}
        >
          {s}
        </li>
      {/each}
    </ul>
  {/if}
</div>
