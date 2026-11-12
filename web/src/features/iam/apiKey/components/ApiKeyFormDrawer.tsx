import { Button, Drawer, Space } from 'antd'
import { Popup } from 'antd-mobile'

import { Platform } from '@shared/platform'

import type { ApiKey, ApiKeyFormValues } from '../types'
import { ApiKeyForm } from './ApiKeyForm'

const FORM_ID = 'api-key-form'

const TITLES = { create: '新建 API Key', edit: '编辑 API Key' } as const

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  initial?: ApiKey
  pending: boolean
  onSubmit: (values: ApiKeyFormValues) => void
  onClose: () => void
}

/** API Key 表单弹层：桌面 Drawer / 移动全屏 Popup（与 iam 其他管理页一致）。 */
export function ApiKeyFormDrawer({
  open,
  mode,
  initial,
  pending,
  onSubmit,
  onClose,
}: Props) {
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
        <Drawer open={open} width={640} title={title} onClose={onClose} footer={footer}>
          {open && (
            <ApiKeyForm
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
              <ApiKeyForm
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
