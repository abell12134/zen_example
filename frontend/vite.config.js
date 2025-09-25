import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: "0.0.0.0", // 允许外部访问
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://43.142.25.125:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist'
  }
})