import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    // Playwright specs have their own runner and must not be collected by Vitest.
    exclude: ['e2e/**', 'node_modules/**', 'dist/**'],
  },
})
