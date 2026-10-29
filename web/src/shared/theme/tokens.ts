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
 * ── 角色约定 ─────────────────────────────────────────────────────────────
 *  · `brand`      品牌原色：**只做品牌露出**（logo、品牌名、登录页光斑）。对白底对比度不足，别当交互色。
 *  · `brandAction` 交互色：主按钮/链接/焦点（antd `colorPrimary`）。需满足白底正文对比度。
 *  · `brandActionText` 交互色**底上的文字**（主按钮白字/深字）。与 `brandAction` 一起决定对比度。
 *  · `brandSoft`  品牌浅底：**只用于品牌面**（登录页）。工作区大面积铺会把界面染成品牌色。
 *  · 工作区用**低饱和画布**（`bgLayout`，可暖可冷）+ 容器（`bgContainer`），品牌色只做点缀。
 *  · 左栏分两层：`bgSystemSidebar`（系统级外框）/ `bgWorkspaceNav`（workspace 菜单），可独立调色。
 *
 * ── 选中态约定 ───────────────────────────────────────────────────────────
 *  · `navSelectedBg` / `navSelectedText` 是**成对**的完整结果，组件直接套用，
 *    **不得**用品牌色/白底自行推导——反色主题（如 `mono`：选中黑底白字）只改这两个值。
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
  /** 橙（当前）：暖米白画布 + 暖炭灰文字，消费级暖调 */
  orange: {
    brand: '#f5822b',
    /** 与 `brand` 同色相；注意与 `brandActionText` 一起过对比度（当前白字约 3.2:1） */
    brandAction: '#D97706',
    brandActionText: '#ffffff',
    brandSoft: '#fdf0e6',
    bgLayout: '#faf7f2',
    bgContainer: '#ffffff',
    bgMuted: '#f3eee7',
    /** 系统级左栏：最深的暖灰，做外框 */
    bgSystemSidebar: '#ebe2d4',
    /** workspace 级左栏：介于系统栏与画布之间，不用纯白 */
    bgWorkspaceNav: '#f5f0e8',
    border: '#ded7cf',
    borderSecondary: '#e7e1d9',
    text: '#2b2622',
    textSecondary: '#6b625a',
    textTertiary: '#8a7f76',
    /** 选中态：`brandAction` 底 + 白字（与主按钮同一组合，对比度约 3.2:1） */
    navSelectedBg: '#D97706',
    navSelectedText: '#ffffff',
  },
  /** 示例第二套：蓝（按需增删） */
  blue: {
    brand: '#1677ff',
    brandAction: '#0958d9',
    brandActionText: '#ffffff',
    brandSoft: '#e8f1ff',
    bgLayout: '#f5f7fa',
    bgContainer: '#ffffff',
    bgMuted: '#eef2f7',
    bgSystemSidebar: '#e6eef7',
    bgWorkspaceNav: '#f0f5fa',
    border: '#d9e2ec',
    borderSecondary: '#e6f0ff',
    text: '#1f2933',
    textSecondary: '#52606d',
    textTertiary: '#8896ab',
    navSelectedBg: '#0958d9',
    navSelectedText: '#ffffff',
  },
  /** 示例第三套：黑白——演示**反色选中态**（未选中黑字，选中黑底白字） */
  mono: {
    brand: '#111111',
    brandAction: '#111111',
    brandActionText: '#ffffff',
    brandSoft: '#f2f2f2',
    bgLayout: '#f5f5f5',
    bgContainer: '#ffffff',
    bgMuted: '#ececec',
    bgSystemSidebar: '#e6e6e6',
    bgWorkspaceNav: '#f0f0f0',
    border: '#d9d9d9',
    borderSecondary: '#e5e5e5',
    text: '#1a1a1a',
    textSecondary: '#595959',
    textTertiary: '#8c8c8c',
    navSelectedBg: '#111111',
    navSelectedText: '#ffffff',
  },
} as const

export type ColorSchemeName = keyof typeof colorSchemes

function resolveColorScheme(name: string): (typeof colorSchemes)[ColorSchemeName] {
  return name in colorSchemes ? colorSchemes[name as ColorSchemeName] : colorSchemes.orange
}

/** 当前生效的配色（由 `config.json` 的 `colorScheme` 选定）。 */
export const colorTokens = resolveColorScheme(appConfig.colorScheme)

/**
 * workspace 级配色：workspace 内部用到的颜色都从这里取（左栏、画布、容器、边框、文字、交互色）。
 * 各 workspace 可在 `workspace.theme` 覆盖任意项，未声明的回退到 `defaultWorkspacePalette`
 * （= 当前全局配色方案）。系统壳不读它，仍走全局品牌配色。
 *
 * 注意：语义色（成功/错误/警告）刻意不在调色板内，跨 workspace 保持一致。
 */
export interface WorkspacePalette {
  /** 左栏：底色 / 分隔线 / 选中项 */
  navBg: string
  navBorder: string
  navSelectedBg: string
  navSelectedText: string
  /** 内容画布 / 容器 / 控件底 */
  canvasBg: string
  containerBg: string
  mutedBg: string
  /** 边框与文字 */
  border: string
  borderSecondary: string
  text: string
  textSecondary: string
  textTertiary: string
  /** 交互色（主按钮/链接/焦点）及其实底文字 */
  action: string
  actionText: string
}

export const defaultWorkspacePalette: WorkspacePalette = {
  navBg: colorTokens.bgWorkspaceNav,
  navBorder: colorTokens.border,
  navSelectedBg: colorTokens.navSelectedBg,
  navSelectedText: colorTokens.navSelectedText,
  canvasBg: colorTokens.bgLayout,
  containerBg: colorTokens.bgContainer,
  mutedBg: colorTokens.bgMuted,
  border: colorTokens.border,
  borderSecondary: colorTokens.borderSecondary,
  text: colorTokens.text,
  textSecondary: colorTokens.textSecondary,
  textTertiary: colorTokens.textTertiary,
  action: colorTokens.brandAction,
  actionText: colorTokens.brandActionText,
}

/** 合并 workspace 覆盖项；无覆盖时直接返回默认（保持引用稳定）。 */
export function resolveWorkspacePalette(
  theme?: Partial<WorkspacePalette>,
): WorkspacePalette {
  return theme ? { ...defaultWorkspacePalette, ...theme } : defaultWorkspacePalette
}
