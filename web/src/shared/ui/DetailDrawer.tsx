import { Drawer } from 'antd'
import { Popup } from 'antd-mobile'
import { useEffect, useRef } from 'react'
import type { ReactNode } from 'react'
import { createPortal } from 'react-dom'

import { Platform } from '@shared/platform'
import { useWorkspaceContextPanel } from '@shared/shell'

interface Props {
  open: boolean
  title: string
  children: ReactNode
  onClose: () => void
}

/**
 * 详情弹层（只读展示）。
 *
 * 在应用壳内：内容 portal 到壳的**非模态上下文面板**（桌面不锁背景，移动为全屏 Popup）。
 * 壳外（无 Provider）保留原 Drawer/Popup 行为。新建/编辑等表单不走这里。
 */
export function DetailDrawer({ open, title, children, onClose }: Props) {
  const panel = useWorkspaceContextPanel()
  const onCloseRef = useRef(onClose)

  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  useEffect(() => {
    if (!panel) return
    if (open) {
      panel.open({ title, onClose: () => onCloseRef.current() })
    } else {
      panel.close({ silent: true })
    }
  }, [open, title, panel])

  useEffect(() => {
    if (!panel) return
    return () => panel.close({ silent: true })
  }, [panel])

  if (panel) {
    if (!open || !panel.container) return null
    return createPortal(children, panel.container)
  }

  return (
    <Platform
      desktop={
        <Drawer open={open} width={640} title={title} onClose={onClose}>
          {children}
        </Drawer>
      }
      mobile={
        <Popup
          visible={open}
          onMaskClick={onClose}
          bodyStyle={{ height: '100vh', overflow: 'auto' }}
        >
          <div
            style={{
              padding: 16,
              fontWeight: 600,
              borderBottom: '1px solid #f0f0f0',
              position: 'sticky',
              top: 0,
              background: '#fff',
            }}
          >
            {title}
          </div>
          <div style={{ padding: 16 }}>{children}</div>
        </Popup>
      }
    />
  )
}
