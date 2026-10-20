import { Form, Input, Modal } from 'antd'
import { useEffect } from 'react'

import type { PermissionFormValues, ResourcePermission } from '../types'

const TITLES = { create: '新增权限', edit: '编辑权限' } as const

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  initial?: ResourcePermission
  pending: boolean
  onSubmit: (values: PermissionFormValues) => void
  onClose: () => void
}

/** 权限表单弹窗（资源聚合内实体）：`action` 是身份，创建后不可改。 */
export function PermissionFormDialog({ open, mode, initial, pending, onSubmit, onClose }: Props) {
  const [form] = Form.useForm<PermissionFormValues>()

  useEffect(() => {
    if (!open) return
    form.setFieldsValue(
      initial
        ? {
            action: initial.action,
            name: initial.name,
            description: initial.description ?? undefined,
          }
        : { action: '', name: '', description: '' },
    )
  }, [open, initial, form])

  return (
    <Modal
      open={open}
      title={TITLES[mode]}
      confirmLoading={pending}
      onOk={() => form.submit()}
      onCancel={onClose}
      okText="保存"
      cancelText="取消"
    >
      <Form form={form} layout="vertical" requiredMark={false} onFinish={onSubmit}>
        <Form.Item
          name="action"
          label="动作"
          rules={[{ required: true, message: '请输入动作' }]}
        >
          <Input maxLength={64} placeholder="如 export / reset-password" disabled={mode === 'edit'} />
        </Form.Item>
        <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
          <Input maxLength={128} placeholder="名称" />
        </Form.Item>
        <Form.Item name="description" label="描述">
          <Input.TextArea rows={3} maxLength={200} placeholder="描述" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
