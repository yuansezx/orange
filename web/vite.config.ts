import { readFileSync, readdirSync, realpathSync, statSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath, URL } from 'node:url'

import react from '@vitejs/plugin-react'
import type { Plugin } from 'vite'
import { defineConfig, loadEnv, normalizePath, searchForWorkspaceRoot } from 'vite'

const resolve = (path: string) => fileURLToPath(new URL(path, import.meta.url))

// 应用版本单一事实源：读 package.json，避免手写漂移
const packageJson = JSON.parse(readFileSync(resolve('./package.json'), 'utf-8')) as {
  version: string
}

/**
 * 目录链接模块的「真实路径 → 宿主链接路径」映射。
 *
 * 模块在 `web/src/features/<name>` 下以目录链接存在，Vite 默认真实路径解析，
 * 会让模块内的裸依赖（antd / dayjs…）从仓外真实路径向上找 node_modules 而失败。
 * 这里只把**链接进来的 feature 目录**改写回宿主路径，其余文件维持默认解析。
 */
interface ModulePathMapping {
  real: string
  linked: string
}

const featureRoot = resolve('./src/features')

const modulePathMappings: ModulePathMapping[] = readdirSync(featureRoot).flatMap((name) => {
  const linked = normalizePath(path.join(featureRoot, name))
  try {
    if (!statSync(linked).isDirectory()) return []
    const real = normalizePath(realpathSync(linked))
    return real === linked ? [] : [{ real, linked }]
  } catch {
    return []
  }
})

// Windows 路径大小写不敏感；其他平台保持严格比较。
const normalizeCase = (value: string) =>
  process.platform === 'win32' ? value.toLowerCase() : value

const isUnder = (id: string, base: string) =>
  normalizeCase(id) === normalizeCase(base)
  || normalizeCase(id).startsWith(`${normalizeCase(base)}/`)

/** 把解析到模块真实路径的 id 改写回宿主链接路径（不改变其他文件的解析）。 */
function modulePathPlugin(mappings: ModulePathMapping[]): Plugin {
  return {
    name: 'orange-module-path',
    enforce: 'post',
    async resolveId(source, importer, options) {
      const resolved = await this.resolve(source, importer, { ...options, skipSelf: true })
      if (!resolved) {
        // 裸依赖从仓外真实路径解析失败：换用宿主链接路径的 importer 再解析一次。
        if (!importer) return null
        const cleanImporter = importer.split('?')[0]
        const mapping = mappings.find((item) => isUnder(cleanImporter, item.real))
        if (!mapping) return null
        const linkedImporter = mapping.linked + cleanImporter.slice(mapping.real.length)
        return this.resolve(source, linkedImporter, { ...options, skipSelf: true })
      }
      const id = normalizePath(resolved.id)
      const mapping = mappings.find((item) => isUnder(id, item.real))
      if (!mapping) return null
      return { ...resolved, id: mapping.linked + id.slice(mapping.real.length) }
    },
  }
}

// https://vite.dev/config/
//
// ORANGE_* 只影响 dev server / 构建，不进入浏览器运行时（前端统一走相对 /api），
// 故不用 VITE_ 前缀，避免被内联进 bundle；代码默认值保证不建 .env 也能跑。
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, resolve('.'), 'ORANGE_')

  // 目录链接进来的模块真身在项目根之外，dev 需显式放行（不硬编码闭源路径）
  const moduleRoots = (env.ORANGE_MODULE_ROOTS ?? '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)

  return {
    plugins: [react(), modulePathPlugin(modulePathMappings)],
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
      // 目录链接模块不得自带第二份 React
      dedupe: ['react', 'react-dom'],
      // 路径别名：@app / @shared / @features 对应组合根 / 共享内核 / 业务模块
      alias: {
        '@app': resolve('./src/app'),
        '@shared': resolve('./src/shared'),
        '@features': resolve('./src/features'),
        '@': resolve('./src'),
      },
    },
    server: {
      host: env.ORANGE_DEV_HOST || '0.0.0.0',
      port: Number(env.ORANGE_DEV_PORT) || 8000,
      fs: {
        allow: [searchForWorkspaceRoot(process.cwd()), ...moduleRoots],
      },
      // 后端不做 CORS，dev 经 vite proxy 转发到 FastAPI（全局前缀 /api）
      proxy: {
        '/api': {
          target: env.ORANGE_API_PROXY_TARGET || 'http://127.0.0.1:8100',
          changeOrigin: true,
        },
      },
    },
  }
})
