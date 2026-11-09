import { Drawer } from 'antd'
import { Popup } from 'antd-mobile'
import type { ReactNode } from 'react'

import { Platform } from '@shared/platform'

interface Props {
  open: boolean
  title: string
  width?: number
  onClose: () => void
  children: ReactNode
}

/** 管理类抽屉：桌面 Drawer / 移动全屏 Popup（表格/列表的容器）。 */
export function ManageDrawer({ open, title, width = 860, onClose, children }: Props) {
  return (
    <Platform
      desktop={
        <Drawer open={open} width={width} title={title} onClose={onClose}>
          {children}
        </Drawer>
      }
      mobile={
        <Popup
          visible={open}
          onMaskClick={onClose}
          bodyStyle={{ height: '100vh', display: 'flex', flexDirection: 'column' }}
        >
          <div style={{ padding: 16, fontWeight: 600, borderBottom: '1px solid #f0f0f0' }}>
            {title}
          </div>
          <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>{children}</div>
        </Popup>
      }
    />
  )
}
