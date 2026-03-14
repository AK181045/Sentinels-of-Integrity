import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'public/popup.html'),
        content_script: resolve(__dirname, 'src/content/content_script.js'),
        service_worker: resolve(__dirname, 'src/background/service_worker.js'),
      },
      output: { entryFileNames: '[name].js' },
    },
  },
});
