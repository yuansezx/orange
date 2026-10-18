import { useQuery } from '@tanstack/react-query'
import { Alert, Button, Drawer, Space, Spin } from 'antd'
import { Popup } from 'antd-mobile'

import { Platform } from '@shared/platform'

import { getUserDetail } from '../api/userApi'
import type { UserFormValues } from '../types'
import { UserForm } from './UserForm'

const FORM_ID = 'user-form'

const TITLES = { create: '新建用户', edit: '编辑用户' } as const

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  /** 编辑时对应用户 id（详情含角色，打开时拉取）。 */
  userId?: string
  pending: boolean
  onSubmit: (values: UserFormValues) => void
  onClose: () => void
}

/**
 * 用户表单弹层：桌面 Drawer / 移动全屏 Popup。
 * 编辑时先拉 `GET /users/{id}/detail`（列表不含角色集），拿到后再挂表单。
 */
export function UserFormDrawer({ open, mode, userId, pending, onSubmit, onClose }: Props) {
  const title = TITLES[mode]
  const { data, isLoading, error } = useQuery({
    queryKey: ['user-detail', userId],
    queryFn: () => getUserDetail(userId as string),
    enabled: open && mode === 'edit' && !!userId,
  })

  const content =
    mode === 'edit' && isLoading ? (
      <Spin />
    ) : error ? (
      <Alert type="error" showIcon message={error.message} />
    ) : open && (mode === 'create' || data) ? (
      <UserForm
        key={userId ?? 'new'}
        formId={FORM_ID}
        mode={mode}
        initial={data}
        onSubmit={onSubmit}
      />
    ) : null

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
          {content}
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
          <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>{content}</div>
          <div style={{ padding: 12, borderTop: '1px solid #f0f0f0', textAlign: 'right' }}>
            {footer}
          </div>
        </Popup>
      }
    />
  )
}
