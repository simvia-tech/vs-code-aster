import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import { resolve } from 'path';

export default defineConfig({
  root: resolve(__dirname),
  base: './',
  resolve: {
    alias: {
      // Share the report types + pure glyph helpers with the extension host,
      // which produces the diagnostics from the same shapes.
      '@report': resolve(__dirname, '../../src/validationReport.ts'),
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
