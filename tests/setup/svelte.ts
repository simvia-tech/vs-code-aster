import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/svelte';

afterEach(() => {
  cleanup();
});

// The webviews talk to the host through the VS Code webview bridge; stub it so
// components that call `acquireVsCodeApi()` at module load don't throw.
type AnyGlobal = typeof globalThis & { acquireVsCodeApi?: () => unknown };
const g = globalThis as AnyGlobal;
if (!g.acquireVsCodeApi) {
  g.acquireVsCodeApi = () => ({
    postMessage: () => {},
    getState: () => undefined,
    setState: () => {},
  });
}

// happy-dom lacks a couple of APIs the components touch.
if (typeof window !== 'undefined') {
  if (!window.matchMedia) {
    window.matchMedia = ((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    })) as typeof window.matchMedia;
  }
  if (!Element.prototype.scrollIntoView) {
    Element.prototype.scrollIntoView = () => {};
  }
}
