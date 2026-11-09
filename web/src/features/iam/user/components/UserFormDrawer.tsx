import { Button, Drawer, Space } from 'antd'
import { Popup } from 'antd-mobile'

import { Platform } from '@shared/platform'

import type { UserFormValues, UserListItem } from '../types'
import { UserForm } from './UserForm'

const FORM_ID = 'user-form'

const TITLES = { create: '新建用户', edit: '编辑用户' } as const

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  /** 编辑时直接用列表行初始化（列表已含表单字段）。 */
  user?: UserListItem
  canAssignRoles: boolean
  pending: boolean
  onSubmit: (values: UserFormValues) => void
  onClose: () => void
}

/**
 * 用户表单弹层：桌面 Drawer / 移动全屏 Popup（与其他管理页一致）。
 * 列表行已包含编辑所需字段；角色改由独立入口管理。
 */
export function UserFormDrawer({
  open,
  mode,
  user,
  canAssignRoles,
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
            <UserForm
              key={user?.id ?? 'new'}
              formId={FORM_ID}
              mode={mode}
              initial={user}
              canAssignRoles={canAssignRoles}
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
              <UserForm
                key={user?.id ?? 'new'}
                formId={FORM_ID}
                mode={mode}
                initial={user}
                canAssignRoles={canAssignRoles}
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
