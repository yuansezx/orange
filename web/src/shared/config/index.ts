import appConfigJson from '@/config.json'

/**
 * 应用元信息——值来自**数据文件**，此处只做"读数据 + 取版本 + 定型"，不含配置值。
 * （对照后端 settings.py：配置是数据（config.yaml），代码负责读它。）
 *
 *  · name        ← src/config.json 的 appName（数据）
 *  · colorScheme ← src/config.json 的 colorScheme（选哪套配色，值域见 @shared/theme/tokens）
 *  · version     ← 构建期由 vite.config.ts 从 package.json 注入（单一事实源，勿手写）
 *
 * version 用 `typeof` 兜底：构建期注入的真值优先，若未注入（见 vite.config.ts 记录的
 * dev 侧框架问题）则回退 'dev'，避免未定义标识符直接 ReferenceError。
 */
export const appConfig = {
  name: appConfigJson.appName,
  colorScheme: appConfigJson.colorScheme,
  version: typeof __APP_VERSION__ === 'undefined' ? 'dev' : __APP_VERSION__,
} as const
