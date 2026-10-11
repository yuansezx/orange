import type { ThemeConfig } from 'antd'

import { colorTokens } from '@shared/theme/tokens'

/**
 * 全局主题——把设计 token（`@shared/theme/tokens`）喂给 antd。
 * 配色改 token 一处即全局生效（含自定义内联样式，它们也引同一份 token）。
 */
export const antdTheme: ThemeConfig = {
  token: {
    colorPrimary: colorTokens.brand,
    borderRadius: 6,
  },
}
