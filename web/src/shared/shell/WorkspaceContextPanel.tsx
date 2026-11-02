import { Button } from 'antd'
import { Popup } from 'antd-mobile'
import { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'

import { Platform } from '@shared/platform'
import { layoutTokens } from '@shared/theme/layout'
import { useWorkspacePalette } from '@shared/theme/workspacePaletteContext'
import { IconX } from '@shared/ui/icons'

import {
  WorkspaceContextPanelContext,
  type WorkspaceContextPanelConfig,
  type WorkspaceContextPanelValue,
} from './workspaceContextPanelContext'
import styles from './shell.module.css'

/**
 * workspace 级上下文面板（context panel）：桌面为**非模态** overlay（无遮罩、背景可操作），移动为全屏 Popup。
 * 内容由 `DetailDrawer` 通过 portal 注入，见 `shared/ui/DetailDrawer`。
 */
export function WorkspaceContextPanelProvider({ children }: { children: ReactNode }) {
  const [container, setContainer] = useState<HTMLDivElement | null>(null)
  const [panel, setPanel] = useState<{ open: boolean; title: string }>({
    open: false,
    title: '',
  })
  const onCloseRef = useRef<(() => void) | null>(null)

  const open = useCallback((config: WorkspaceContextPanelConfig) => {
    onCloseRef.current = config.onClose
    setPanel({ open: true, title: config.title })
  }, [])

  const close = useCallback((options?: { silent?: boolean }) => {
    setPanel((prev) => (prev.open ? { ...prev, open: false } : prev))
    if (options?.silent) {
      onCloseRef.current = null
      return
    }
    const onClose = onCloseRef.current
    onCloseRef.current = null
    onClose?.()
  }, [])

  const value = useMemo<WorkspaceContextPanelValue>(
    () => ({
      container,
      isOpen: panel.open,
      title: panel.title,
      open,
      close,
      setContainer,
    }),
    [container, panel.open, panel.title, open, close],
  )

  return (
    <WorkspaceContextPanelContext.Provider value={value}>
      {children}
    </WorkspaceContextPanelContext.Provider>
  )
}

function useWorkspaceContextPanelValue(): WorkspaceContextPanelValue {
  const value = useContext(WorkspaceContextPanelContext)
  if (!value) {
    throw new Error('WorkspaceContextPanel 必须在 WorkspaceContextPanelProvider 内使用')
  }
  return value
}

export function WorkspaceContextPanel() {
  const { isOpen, title, close, setContainer } = useWorkspaceContextPanelValue()
  const palette = useWorkspacePalette()

  useEffect(() => {
    if (!isOpen) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') close()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [isOpen, close])

  const header = (
    <div
      style={{
        height: layoutTokens.headerHeight,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-start',
        gap: 8,
        paddingInline: 16,
        borderBottom: `1px solid ${palette.borderSecondary}`,
        background: palette.containerBg,
      }}
    >
      <Button
        type="text"
        icon={<IconX size={16} />}
        aria-label="关闭上下文面板"
        onClick={() => close()}
      />
      <span
        style={{
          fontWeight: 600,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {title}
      </span>
    </div>
  )

  return (
    <Platform
      desktop={
        <aside
          className={styles.workspaceContextPanel}
          data-open={isOpen}
          aria-hidden={!isOpen}
          style={{
            width: layoutTokens.workspaceContextPanelWidth,
            // 窄桌面时别盖住系统侧栏（按展开宽度保守预留）与 workspace 侧栏
            maxWidth: `calc(100vw - ${layoutTokens.systemSidebarExpandedWidth + layoutTokens.workspaceSidebarWidth + 20}px)`,
            background: palette.containerBg,
            borderLeft: `1px solid ${palette.borderSecondary}`,
            boxShadow: '-8px 0 24px rgba(0, 0, 0, 0.08)',
          }}
        >
          {header}
          <div ref={setContainer} className={styles.contextPanelBody} />
        </aside>
      }
      mobile={
        <Popup
          visible={isOpen}
          position="right"
          onMaskClick={() => close()}
          bodyStyle={{
            width: '100vw',
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            background: palette.containerBg,
          }}
        >
          {header}
          <div
            ref={setContainer}
            style={{ flex: 1, minHeight: 0, overflow: 'auto', padding: 16 }}
          />
        </Popup>
      }
    />
  )
}
