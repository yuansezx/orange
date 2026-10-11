import { appConfig } from '@shared/config'

/**
 * 设计 token —— 配色的唯一来源。
 *
 * · `colorSchemes`：**保留多套配色方案**，键名即 `src/config.json` 里 `colorScheme` 的可选值。
 * · `colorTokens` ：**当前生效**的那套（由 config 选定，非法/缺省回退 `orange`）。
 *
 * 消费方（`app/theme.ts`、各布局内联样式）一律引 `colorTokens`，**别写死 hex**。
 * 之所以自建而非用 antd 的 CSS 变量：本项目同时用 antd 与 antd-mobile（两套主题系统），
 * 需要两家之上的共同来源才能收敛到一处。
 *
 * 说明：config 是**构建期**的，换方案 = 改 `colorScheme` 后**重新构建**（非运行时切换）。
 *
 * ── 组织约定（将来会演进，先记住这个问题）────────────────────────────────
 *  · **配置只放"选哪套"（一个旋钮），不放值**；值都在代码。
 *  · 目前**只有颜色**，所以叫 `colorSchemes` + config 的 `colorScheme`。
 *  · 将来加字体/圆角等类别时：**有多个变体的类别**（颜色、字体族…）收进"主题方案"，
 *    升级为 `themes = { <name>: { colors, typography, radius } }`，config **仍只有一个 `theme` 选择**；
 *    **只有一套的类别**（间距、层级 z-index、动画时长）**独立一份、不进主题**（否则每主题复制冗余）。
 *  · 即"**多类 token 合到一个主题旋钮**"，而非"每类一个 config"——除非真要跨维度任意组合（罕见）。
 *    （此结论非定论；将来需求变可改，但要知道当初是这么想的。）
 */
export const colorSchemes = {
  /** 橙（当前） */
  orange: {
    brand: '#f5822b',
    bgContainer: '#ffffff',
    borderSecondary: '#f0f0f0',
    textTertiary: '#999999',
  },
  /** 示例第二套：蓝（按需增删） */
  blue: {
    brand: '#1677ff',
    bgContainer: '#ffffff',
    borderSecondary: '#e6f0ff',
    textTertiary: '#8896ab',
  },
} as const

export type ColorSchemeName = keyof typeof colorSchemes

function resolveColorScheme(name: string): (typeof colorSchemes)[ColorSchemeName] {
  return name in colorSchemes ? colorSchemes[name as ColorSchemeName] : colorSchemes.orange
}

/** 当前生效的配色（由 `config.json` 的 `colorScheme` 选定）。 */
export const colorTokens = resolveColorScheme(appConfig.colorScheme)
