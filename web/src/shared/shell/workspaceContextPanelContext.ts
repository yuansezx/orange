import { createContext, useContext } from 'react'

export interface WorkspaceContextPanelConfig {
  title: string
  onClose: () => void
}

export interface WorkspaceContextPanelValue {
  container: HTMLDivElement | null
  isOpen: boolean
  title: string
  open: (config: WorkspaceContextPanelConfig) => void
  /** `silent`：组件卸载/页面主动关闭时只收起面板，不回调页面的 onClose。 */
  close: (options?: { silent?: boolean }) => void
  setContainer: (element: HTMLDivElement | null) => void
}

export const WorkspaceContextPanelContext = createContext<WorkspaceContextPanelValue | null>(null)

/** 页面/详情组件取用；不在壳内时返回 null（退化为旧的 DetailDrawer 行为）。 */
export function useWorkspaceContextPanel(): WorkspaceContextPanelValue | null {
  return useContext(WorkspaceContextPanelContext)
}
