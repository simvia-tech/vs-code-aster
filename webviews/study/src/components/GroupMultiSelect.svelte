<script lang="ts">
  import type { GroupKindTag } from '@scenario/studyMeta';
  import type { TaggedGroup } from '../lib/draft';
  import MultiSelect from '../../../shared/components/ui/MultiSelect.svelte';

  let {
    label,
    candidates,
    selected,
    freeTextKind,
    hint = '',
    required = false,
    id,
    onChange,
  }: {
    label: string;
    candidates: TaggedGroup[];
    selected: TaggedGroup[];
    freeTextKind: GroupKindTag;
    hint?: string;
    required?: boolean;
    id?: string;
    onChange: (groups: TaggedGroup[]) => void;
  } = $props();

  function toggleByName(name: string) {
    if (selected.some((g) => g.name === name)) {
      onChange(selected.filter((g) => g.name !== name));
    } else {
      const candidate = candidates.find((g) => g.name === name);
      if (candidate) {
        onChange([...selected, candidate]);
      }
    }
  }

  function applyFreeText(value: string) {
    const groups = value
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((name) => ({ name, kind: freeTextKind }));
    onChange(groups);
  }
</script>

<div {id} class="flex flex-col gap-1" style="scroll-margin: 1rem">
  <span class="text-sm text-ui-text-secondary">
    {label}{#if required}<span style="color: var(--vscode-errorForeground, #d45858)"> *</span>{/if}
  </span>
  {#if candidates.length > 0}
    <MultiSelect
      options={candidates.map((g) => ({ value: g.name, label: g.name, hint: g.kind }))}
      selected={selected.map((g) => g.name)}
      onToggle={toggleByName}
      placeholder="Select groups…"
    />
  {:else}
    <input
      type="text"
      class="rounded border border-ui-input-border bg-ui-input-bg px-2 py-1 text-ui-input-fg"
      placeholder="Comma-separated group names"
      value={selected.map((g) => g.name).join(', ')}
      oninput={(e) => applyFreeText((e.currentTarget as HTMLInputElement).value)}
    />
  {/if}
  {#if hint}
    <span class="text-xs text-ui-text-muted">{hint}</span>
  {/if}
</div>
