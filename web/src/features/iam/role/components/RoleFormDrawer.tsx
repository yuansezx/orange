import { Button, Drawer, Space } from 'antd'
import { Popup } from 'antd-mobile'

import { Platform } from '@shared/platform'

import type { RoleDetail, RoleFormValues } from '../types'
import { RoleForm } from './RoleForm'

const FORM_ID = 'role-form'

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  /** 编辑时已拉取的角色详情（含权限/部门集）。 */
  initial?: RoleDetail
  pending: boolean
  onSubmit: (values: RoleFormValues, permissionIds: string[]) => void
  onClose: () => void
}

/**
 * 角色表单弹层：同一份 `RoleForm`，桌面 Drawer / 移动全屏 Popup（平台分叉收口于此）。
 * 仅在 `open` 时挂载表单 → 每次打开按 `initial` 全新初始化，无需 effect 回填。
 */
export function RoleFormDrawer({ open, mode, initial, pending, onSubmit, onClose }: Props) {
  const title = mode === 'edit' ? '编辑角色' : '新建角色'

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
            <RoleForm
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
              <RoleForm
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
