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

  // A group name can repeat across kinds (e.g. a "CloisonSymetrieX" surface AND
  // node group), so options are keyed by a unique `kind:name`, not the bare
  // name — otherwise the dropdown's keyed {#each} hits duplicate keys.
  const keyOf = (g: TaggedGroup) => `${g.kind}:${g.name}`;

  function toggle(key: string) {
    const candidate = candidates.find((g) => keyOf(g) === key);
    if (!candidate) {
      return;
    }
    if (selected.some((g) => keyOf(g) === key)) {
      onChange(selected.filter((g) => keyOf(g) !== key));
    } else {
      onChange([...selected, candidate]);
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
      options={candidates.map((g) => ({ value: keyOf(g), label: g.name, hint: g.kind }))}
      selected={selected.map(keyOf)}
      onToggle={toggle}
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
