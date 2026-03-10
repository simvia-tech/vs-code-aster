import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import { resolve } from 'path';

export default defineConfig({
  root: resolve(__dirname),
  base: './',
  build: {
    outDir: resolve(__dirname, 'dist'),
    emptyOutDir: true,
  },
  plugins: [svelte(), tailwindcss()],
});
