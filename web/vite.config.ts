import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const resolve = (path: string) => fileURLToPath(new URL(path, import.meta.url))

// 应用版本单一事实源：读 package.json，避免手写漂移
const packageJson = JSON.parse(readFileSync(resolve('./package.json'), 'utf-8')) as {
  version: string
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // 构建期把 __APP_VERSION__ 注入为编译常量（全局声明见 src/env.d.ts）。
  //
  // ⚠️ 已知（框架）问题：本环境 vite 8.3.4 的 **dev 下 define 未生效**——
  //    文档称"dev 下作为全局注入"，实测既不替换源码、也不注入全局（build 侧正常）。
  //    故 shared/config 侧用 `typeof` 兜底默认值（dev 显示 'dev'，不崩溃），
  //    不另加自定义插件掩盖；若将来 Vite 修好 dev 注入，此兜底自动失效、无需改动。
  define: {
    __APP_VERSION__: JSON.stringify(packageJson.version),
  },
  resolve: {
    // 路径别名：@app / @shared / @features 对应组合根 / 共享内核 / 业务模块
    alias: {
      '@app': resolve('./src/app'),
      '@shared': resolve('./src/shared'),
      '@features': resolve('./src/features'),
      '@': resolve('./src'),
    },
  },
  server: {
    port: 40000,
    // 后端不做 CORS，dev 经 vite proxy 转发到 FastAPI（模块前缀 /iam）
    proxy: {
      '/iam': {
        target: 'http://127.0.0.1:41000',
        changeOrigin: true,
      },
    },
  },
})
