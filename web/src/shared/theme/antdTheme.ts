import type { ThemeConfig } from 'antd'

import type { WorkspacePalette } from './tokens'

/**
 * 把一套调色板映射成 antd 主题。
 *
 * 全局主题（系统壳）用 `defaultWorkspacePalette`；workspace 用合并后的调色板套一层
 * 嵌套 `ConfigProvider`，antd 组件在 workspace 内自动切换，页面代码不用感知。
 */
export function buildAntdTheme(palette: WorkspacePalette): ThemeConfig {
  return {
    token: {
      colorPrimary: palette.action,
      colorBgLayout: palette.canvasBg,
      colorBgContainer: palette.containerBg,
      colorBgElevated: palette.containerBg,
      colorBorder: palette.border,
      colorBorderSecondary: palette.borderSecondary,
      colorText: palette.text,
      colorTextSecondary: palette.textSecondary,
      colorTextTertiary: palette.textTertiary,
      borderRadius: 6,
    },
    components: {
      Button: {
        primaryColor: palette.actionText,
        // 默认按钮（取消等）hover/active 走中性色，别和主操作抢强调色
        defaultHoverBg: palette.mutedBg,
        defaultHoverColor: palette.text,
        defaultHoverBorderColor: palette.border,
        defaultActiveBg: palette.borderSecondary,
        defaultActiveColor: palette.text,
        defaultActiveBorderColor: palette.textTertiary,
      },
      Menu: {
        itemSelectedBg: palette.navSelectedBg,
        itemSelectedColor: palette.navSelectedText,
      },
      Segmented: {
        trackBg: palette.mutedBg,
      },
    },
  }
}
