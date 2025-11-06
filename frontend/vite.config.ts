import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 抑制来自 node_modules 的弃用警告
        // 这些警告来自第三方库（如 Bootstrap），我们无法直接修改
        quietDeps: true,
        // 注意：silenceDeprecations 需要通过 Sass API 设置
        // 如果 quietDeps 不够，可以通过环境变量 SASS_SILENCE_DEPRECATIONS 来抑制
        // 在 package.json 的脚本中设置：SASS_SILENCE_DEPRECATIONS=import,global-builtin,color-functions
      }
    }
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/graphql': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
});

