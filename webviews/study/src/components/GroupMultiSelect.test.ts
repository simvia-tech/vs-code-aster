import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import GroupMultiSelect from './GroupMultiSelect.svelte';
import type { TaggedGroup } from '../lib/draft';

// A real mesh (e.g. ssnv106a.med) names the same group across kinds — here
// "Shared" is both a surface and a node group. The dropdown must key by
// kind:name so the keyed {#each} doesn't crash on duplicate keys.
const candidates: TaggedGroup[] = [
  { name: 'Shared', kind: 'surface' },
  { name: 'Shared', kind: 'node' },
  { name: 'OnlyNode', kind: 'node' },
];

describe('GroupMultiSelect with names repeated across kinds', () => {
  it('opens the dropdown and renders both same-named options (no duplicate-key crash)', async () => {
    render(GroupMultiSelect, {
      props: {
        label: 'Constrained groups',
        candidates,
        selected: [],
        freeTextKind: 'node',
        onChange: () => {},
      },
    });
    await fireEvent.click(screen.getByRole('button'));
    expect(screen.getAllByText('Shared')).toHaveLength(2);
    expect(screen.getByText('OnlyNode')).toBeTruthy();
  });

  it('toggles the exact (name, kind) pair, not just the name', async () => {
    const onChange = vi.fn();
    render(GroupMultiSelect, {
      props: {
        label: 'Constrained groups',
        candidates,
        selected: [],
        freeTextKind: 'node',
        onChange,
      },
    });
    await fireEvent.click(screen.getByRole('button'));
    const boxes = screen.getAllByRole('checkbox');
    await fireEvent.click(boxes[0]); // the surface "Shared"
    expect(onChange).toHaveBeenCalledWith([{ name: 'Shared', kind: 'surface' }]);
  });
});
