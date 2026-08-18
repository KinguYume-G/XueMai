import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        secure: false,
        // 🔥 支持 Server-Sent Events (SSE) 流式响应
        configure: (proxy, options) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 确保流式响应头正确传递（只修改响应，不修改请求）
            if (req.url?.includes('/stream')) {
              proxyRes.headers['content-type'] = 'text/event-stream'
              proxyRes.headers['cache-control'] = 'no-cache'
              proxyRes.headers['connection'] = 'keep-alive'
              proxyRes.headers['x-accel-buffering'] = 'no'

              // 禁用响应压缩，保持流式传输
              delete proxyRes.headers['content-encoding']
            }
          })
        },
        // 增加超时时间以支持长连接流式响应
        timeout: 0,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
