/// <reference types="vite/client" />

/**
 * 构建期注入的常量（见 vite.config.ts 的 define）。
 * 声明为 `string | undefined`：dev 下可能未注入，故允许 undefined 以便 `typeof` 兜底。
 */
declare const __APP_VERSION__: string | undefined
