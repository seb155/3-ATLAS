import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0', // Bind to all interfaces for Docker
    strictPort: true, // Exit if port is already in use
    // Allow access from custom domains (axoiq.com for production-like local setup)
    allowedHosts: ['nexus.axoiq.com', 'nexus.localhost'],
    watch: {
      usePolling: true, // Enable polling for Docker file watching (Windows/WSL)
      interval: 1000, // Poll every second
    },
  },
})
