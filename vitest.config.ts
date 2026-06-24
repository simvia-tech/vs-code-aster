import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { svelteTesting } from '@testing-library/svelte/vite';
import { resolve } from 'path';

// One Vitest install, three projects with isolated environments:
//   unit   — extension-host pure logic + scenario generators (Node env). The
//            `vscode` module is neutralized by a faithful stub so modules that
//            construct Uri/Range/Diagnostic can run outside the extension host.
//   viewer — Svelte webview unit/component tests (happy-dom).
//   export — Svelte webview unit/component tests (happy-dom).
export default defineConfig({
  test: {
    projects: [
      {
        resolve: {
          alias: {
            vscode: resolve(__dirname, 'tests/stubs/vscode.ts'),
          },
        },
        test: {
          name: 'unit',
          environment: 'node',
          include: ['tests/unit/**/*.test.ts', 'src/scenario/**/*.test.ts'],
        },
      },
      {
        plugins: [svelte()],
        test: {
          name: 'viewer',
          environment: 'happy-dom',
          include: ['webviews/viewer/src/**/*.test.ts'],
          setupFiles: ['tests/setup/svelte.ts'],
        },
      },
      {
        plugins: [svelte()],
        test: {
          name: 'export',
          environment: 'happy-dom',
          include: ['webviews/export/src/**/*.test.ts'],
          setupFiles: ['tests/setup/svelte.ts'],
        },
      },
      {
        plugins: [svelte(), svelteTesting()],
        resolve: {
          alias: {
            '@scenario': resolve(__dirname, 'src/scenario'),
          },
        },
        test: {
          name: 'study',
          environment: 'happy-dom',
          include: ['webviews/study/src/**/*.test.ts'],
          setupFiles: ['tests/setup/svelte.ts'],
        },
      },
    ],
  },
});
