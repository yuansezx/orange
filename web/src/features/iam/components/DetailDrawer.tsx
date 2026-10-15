import { Drawer } from 'antd'
import { Popup } from 'antd-mobile'
import type { ReactNode } from 'react'

import { Platform } from '@shared/platform'

interface Props {
  open: boolean
  title: string
  children: ReactNode
  onClose: () => void
}

/** 详情弹层（只读展示）：桌面 Drawer / 移动全屏 Popup——与表单弹层分叉同构，收口于此。 */
export function DetailDrawer({ open, title, children, onClose }: Props) {
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
