import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/doctors': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/appointments': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/doctor_availability': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})