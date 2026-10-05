import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 代理 /api 与 /uploads 到后端 8000（见施工规范 §7.3）
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/uploads': { target: 'http://127.0.0.1:8000', changeOrigin: true }
    }
  }
})
