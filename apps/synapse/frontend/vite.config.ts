/// <reference types="vitest" />
import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: 4000,
      host: '0.0.0.0',
      // Allow access from custom domains (axoiq.com for production-like local setup)
      allowedHosts: ['synapse.axoiq.com', 'synapse.localhost'],
      proxy: {
        '/api/v1': {
          target: 'http://synapse-backend:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    plugins: [react()],
    test: {
      globals: true,
      environment: 'happy-dom',
      setupFiles: './setupTests.ts',
      exclude: ['**/node_modules/**', '**/e2e/**', '**/*.spec.ts'],
    },
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      __APP_VERSION__: JSON.stringify('0.2.2'),
      __GIT_HASH__: JSON.stringify('dev'),
      __BUILD_DATE__: JSON.stringify(new Date().toISOString()),
      __BUILD_NUMBER__: JSON.stringify(Math.floor(Date.now() / 1000).toString()),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  };
});
