import { Form, Input, Select } from 'antd'

import { STATUS_OPTIONS } from '../../constants'
import type { Resource, ResourceFormValues } from '../types'

interface Props {
  formId: string
  mode: 'create' | 'edit'
  initial?: Resource
  onSubmit: (values: ResourceFormValues) => void
}

/**
 * 资源表单（新建 / 编辑共用）。`module` / `code` 是身份，创建后不可改。
 * 由外层以 `key` 重挂，`initialValues` 即可完成初始化。
 */
export function ResourceForm({ formId, mode, initial, onSubmit }: Props) {
  return (
    <Form
      id={formId}
      layout="vertical"
      requiredMark={false}
      initialValues={
        mode === 'edit' && initial
          ? {
              module: initial.module,
              code: initial.code,
              name: initial.name,
              description: initial.description ?? undefined,
              status: initial.status,
            }
          : { status: 'active' }
      }
      onFinish={onSubmit}
    >
      <Form.Item
        name="module"
        label="模块"
        rules={[{ required: true, message: '请输入模块代号' }]}
      >
        <Input maxLength={32} placeholder="如 iam / monitor" disabled={mode === 'edit'} />
      </Form.Item>
      <Form.Item
        name="code"
        label="资源标识"
        rules={[{ required: true, message: '请输入资源标识' }]}
      >
        <Input maxLength={32} placeholder="模块内唯一，创建后不可改（如 report）" disabled={mode === 'edit'} />
      </Form.Item>
      <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
        <Input maxLength={64} placeholder="名称" />
      </Form.Item>
      <Form.Item name="description" label="描述">
        <Input.TextArea rows={3} maxLength={200} placeholder="描述" />
      </Form.Item>
      <Form.Item name="status" label="状态" rules={[{ required: true }]}>
        <Select options={STATUS_OPTIONS} />
      </Form.Item>
    </Form>
  )
}
