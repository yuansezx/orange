import { Button, Drawer, Form, Space } from 'antd'
import { Popup } from 'antd-mobile'
import { useEffect } from 'react'

import { Platform } from '@shared/platform'

import { DeptForm } from './DeptForm'
import type { Dept, DeptFormValues } from '../types'

const TITLES = { create: '新建部门', edit: '编辑部门' } as const

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  dept?: Dept
  parentId?: string
  excludeIds?: string[]
  pending: boolean
  onSubmit: (values: DeptFormValues) => void
  onClose: () => void
}

/** 部门表单弹层：同一份 `DeptForm`，桌面 Drawer / 移动全屏 Popup（与其他管理页一致）。 */
export function DeptFormDrawer({
  open,
  mode,
  dept,
  parentId,
  excludeIds,
  pending,
  onSubmit,
  onClose,
}: Props) {
  const [form] = Form.useForm<DeptFormValues>()

  useEffect(() => {
    if (!open) return
    if (mode === 'edit' && dept) {
      form.setFieldsValue({
        name: dept.name,
        parent_id: dept.parent_id ?? undefined,
        leader_id: dept.leader_id ?? undefined,
        email: dept.email ?? undefined,
        phone: dept.phone ?? undefined,
        description: dept.description ?? undefined,
        status: dept.status,
      })
    } else {
      form.resetFields()
      form.setFieldsValue({ parent_id: parentId, status: 'active' })
    }
  }, [open, mode, dept, parentId, form])

  const submit = async () => {
    const values = await form.validateFields()
    onSubmit(values)
  }

  const title = TITLES[mode]
  const footer = (
    <Space>
      <Button onClick={onClose}>取消</Button>
      <Button type="primary" loading={pending} onClick={submit}>
        保存
      </Button>
    </Space>
  )

  return (
    <Platform
      desktop={
        <Drawer open={open} width={520} title={title} onClose={onClose} footer={footer}>
          {open && <DeptForm form={form} excludeIds={excludeIds} />}
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
            {open && <DeptForm form={form} excludeIds={excludeIds} />}
          </div>
          <div style={{ padding: 12, borderTop: '1px solid #f0f0f0', textAlign: 'right' }}>
            {footer}
          </div>
        </Popup>
      }
    />
  )
}
