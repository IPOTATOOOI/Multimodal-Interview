import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const envDir = path.resolve(__dirname, '..')
  const env = loadEnv(mode, envDir, '')
  const qwenBaseUrl = env.QWEN_BASE_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1'

  return {
    envDir,
    plugins: [vue(), tailwindcss()],
    define: {
      __QWEN_MODEL__: JSON.stringify(env.QWEN_MODEL || 'qwen-plus'),
    },
    resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // 确保路径映射正确
      '@/docx-editor': path.resolve(__dirname, './src/docx-editor'), // docx-editor 模块别名
    },
  },
  server: {
    proxy: {
      '/rss-proxy/infoq': {
        target: 'https://www.infoq.cn',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/infoq/, '/feed'),
      },
      // 开源中国分类源 - 使用路径参数
      '/rss-proxy/oschina-llm': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-llm/, '/groups/rss/llm'),
      },
      '/rss-proxy/oschina-front': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-front/, '/groups/rss/cross-front'),
      },
      '/rss-proxy/oschina-skill': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-skill/, '/groups/rss/skill'),
      },
      '/rss-proxy/oschina-db': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-db/, '/groups/rss/database'),
      },
      '/rss-proxy/oschina-arch': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-arch/, '/groups/rss/architecture'),
      },
      '/rss-proxy/oschina-ai': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-ai/, '/groups/rss/ai-bigdata'),
      },
      '/rss-proxy/oschina-ops': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-ops/, '/groups/rss/ops'),
      },
      '/rss-proxy/oschina-test': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-test/, '/groups/rss/test'),
      },
      '/rss-proxy/oschina-network': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-network/, '/groups/rss/network'),
      },
      '/rss-proxy/oschina-game': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina-game/, '/groups/rss/game'),
      },
      '/rss-proxy/oschina-blockchain': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) =>
          path.replace(/^\/rss-proxy\/oschina-blockchain/, '/groups/rss/blockchain'),
      },

      // 开源中国通用源
      '/rss-proxy/oschina': {
        target: 'https://www.oschina.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/oschina/, '/news/rss'),
      },
      // 36氪
      '/rss-proxy/36kr': {
        target: 'https://36kr.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/36kr/, '/feed'),
      },
      // 极客公园
      '/rss-proxy/geekpark': {
        target: 'http://www.geekpark.net',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/geekpark/, '/rss'),
      },
      // 虎嗅网
      '/rss-proxy/huxiu': {
        target: 'https://www.huxiu.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rss-proxy\/huxiu/, '/rss/0.xml'),
      },
      '/api/v1/workflows/run': {
        target: env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/serpapi': {
        target: 'https://serpapi.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/serpapi/, ''),
      },
      '/qwen': {
        target: qwenBaseUrl,
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/qwen/, ''),
        headers: {
          Authorization: `Bearer ${env.QWEN_API_KEY || ''}`,
        },
      },
    },
  },
  }
})
