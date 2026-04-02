import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
        // Proxy API requests to your local FastAPI backend
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
    },
  },
});
