import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import App from './App.svelte';

describe('study webview App', () => {
  it('renders the form and an initial in-pane preview', () => {
    const { getByText, container } = render(App);
    expect(getByText(/Generate study from scenario/)).toBeTruthy();
    // The default draft previews a linear-static study generated in-bundle.
    const preview = container.querySelector('pre')?.textContent ?? '';
    expect(preview).toContain('DEBUT');
    expect(preview).toContain('MECA_STATIQUE');
  });
});
