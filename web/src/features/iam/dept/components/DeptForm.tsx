import { Form, Input, Select } from 'antd'
import type { FormInstance } from 'antd'

import { DeptTreeSelect } from '../../components/DeptTreeSelect'
import { UserSelect } from '../../components/UserSelect'
import { STATUS_OPTIONS } from '../../constants'
import type { DeptFormValues } from '../types'

interface Props {
  form: FormInstance<DeptFormValues>
  mode: 'create' | 'edit'
  /** 编辑时禁用自身及子孙作为父节点（防环）。 */
  excludeIds?: string[]
}

/** 部门表单字段（两端共用）；提交/取值由外层 Dialog 承担。 */
export function DeptForm({ form, mode, excludeIds }: Props) {
  return (
    <Form form={form} layout="vertical" requiredMark={false}>
      <Form.Item
        name="name"
        label="部门名称"
        rules={[{ required: true, message: '请输入部门名称' }]}
      >
        <Input maxLength={50} placeholder="部门名称" />
      </Form.Item>
      <Form.Item name="parent_id" label="上级部门">
        <DeptTreeSelect excludeIds={excludeIds} placeholder="不选则为根部门" />
      </Form.Item>
      <Form.Item name="leader_id" label="负责人">
        <UserSelect />
      </Form.Item>
      <Form.Item name="email" label="邮箱" rules={[{ type: 'email', message: '邮箱格式不正确' }]}>
        <Input placeholder="邮箱" />
      </Form.Item>
      <Form.Item name="phone" label="手机号">
        <Input placeholder="手机号" />
      </Form.Item>
      <Form.Item name="description" label="描述">
        <Input.TextArea rows={2} maxLength={200} placeholder="描述" />
      </Form.Item>
      {mode === 'edit' && (
        <Form.Item name="status" label="状态">
          <Select options={STATUS_OPTIONS} placeholder="状态" />
        </Form.Item>
      )}
    </Form>
  )
}
