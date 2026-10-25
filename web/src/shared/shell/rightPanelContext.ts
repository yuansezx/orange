import { createContext, useContext } from 'react'

export interface ShellRightPanelConfig {
  title: string
  onClose: () => void
}

export interface ShellRightPanelValue {
  container: HTMLDivElement | null
  isOpen: boolean
  title: string
  open: (config: ShellRightPanelConfig) => void
  /** `silent`：组件卸载/页面主动关闭时只收起面板，不回调页面的 onClose。 */
  close: (options?: { silent?: boolean }) => void
  setContainer: (element: HTMLDivElement | null) => void
}

export const ShellRightPanelContext = createContext<ShellRightPanelValue | null>(null)

/** 页面/详情组件取用；不在壳内时返回 null（退化为旧的 DetailDrawer 行为）。 */
export function useShellRightPanel(): ShellRightPanelValue | null {
  return useContext(ShellRightPanelContext)
}
