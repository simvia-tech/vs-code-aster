import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import { resolve } from 'path';

export default defineConfig({
  root: resolve(__dirname),
  base: './',
  resolve: {
    alias: {
      // The pure study generators live in the extension-host source tree but
      // are vscode-free, so the webview bundle imports them directly for an
      // instant in-pane preview (no host round-trip).
      '@scenario': resolve(__dirname, '../../src/scenario'),
    },
  },
  build: {
    outDir: resolve(__dirname, 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/index.[ext]',
      },
    },
  },
  plugins: [svelte(), tailwindcss()],
});
