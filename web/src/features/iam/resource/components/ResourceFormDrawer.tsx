import { Button, Drawer, Space } from 'antd'
import { Popup } from 'antd-mobile'

import { Platform } from '@shared/platform'

import type { Resource, ResourceFormValues } from '../types'
import { ResourceForm } from './ResourceForm'

const FORM_ID = 'resource-form'

const TITLES = { create: '新建资源', edit: '编辑资源' } as const

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  initial?: Resource
  pending: boolean
  onSubmit: (values: ResourceFormValues) => void
  onClose: () => void
}

/** 资源表单弹层：同一份表单，桌面 Drawer / 移动全屏 Popup。 */
export function ResourceFormDrawer({ open, mode, initial, pending, onSubmit, onClose }: Props) {
  const title = TITLES[mode]

  const footer = (
    <Space>
      <Button onClick={onClose}>取消</Button>
      <Button type="primary" htmlType="submit" form={FORM_ID} loading={pending}>
        保存
      </Button>
    </Space>
  )

  return (
    <Platform
      desktop={
        <Drawer open={open} width={520} title={title} onClose={onClose} footer={footer}>
          {open && (
            <ResourceForm
              key={initial?.id ?? 'new'}
              formId={FORM_ID}
              mode={mode}
              initial={initial}
              onSubmit={onSubmit}
            />
          )}
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
          <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
            {open && (
              <ResourceForm
                key={initial?.id ?? 'new'}
                formId={FORM_ID}
                mode={mode}
                initial={initial}
                onSubmit={onSubmit}
              />
            )}
          </div>
          <div style={{ padding: 12, borderTop: '1px solid #f0f0f0', textAlign: 'right' }}>
            {footer}
          </div>
        </Popup>
      }
    />
  )
}
