import { ConfigProvider } from 'antd'
import { useMemo } from 'react'
import type { ReactNode } from 'react'

import { buildAntdTheme } from './antdTheme'
import type { WorkspacePalette } from './tokens'
import { WorkspacePaletteContext } from './workspacePaletteContext'

interface Props {
  palette: WorkspacePalette
  children: ReactNode
}

/**
 * workspace 作用域主题：
 * · context 给自定义内联样式；
 * · 嵌套 ConfigProvider 让 antd 组件（表格/弹窗/抽屉/下拉）跟随 workspace 配色。
 * 系统壳在 provider 之外，继续用全局品牌配色。
 */
export function WorkspaceThemeProvider({ palette, children }: Props) {
  const theme = useMemo(() => buildAntdTheme(palette), [palette])

  return (
    <WorkspacePaletteContext.Provider value={palette}>
      <ConfigProvider theme={theme}>{children}</ConfigProvider>
    </WorkspacePaletteContext.Provider>
  )
}
