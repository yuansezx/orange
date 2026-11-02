import { Form, Input, Select } from 'antd'
import { useState } from 'react'

import { DeptTreeMultiSelect } from '../../components/DeptTreeMultiSelect'
import { DATA_SCOPE_OPTIONS, STATUS_OPTIONS } from '../../constants'
import type { Role, RoleFormValues } from '../types'
import { PermissionTree } from './PermissionTree'

interface Props {
  /** 供抽屉底部的原生 submit 按钮 `form=` 关联。 */
  formId: string
  mode: 'create' | 'edit'
  initial?: Role
  onSubmit: (values: RoleFormValues, permissionIds: string[]) => void
}

/**
 * 角色表单字段（新建 / 编辑共用，提交由外层抽屉承担）。
 * 由外层以 `key` 重挂，故用 `initialValues` + `useState(initial)` 初始化即可，无需 effect 回填。
 * （只读详情另见 `RoleDetailDrawer`，不复用本表单。）
 */
export function RoleForm({ formId, mode, initial, onSubmit }: Props) {
  const [form] = Form.useForm<RoleFormValues>()
  const dataScope = Form.useWatch('data_scope', form)
  const [permissionIds, setPermissionIds] = useState<string[]>(initial?.permission_ids ?? [])

  return (
    <Form
      id={formId}
      form={form}
      layout="vertical"
      requiredMark={false}
      initialValues={
        mode === 'edit' && initial
          ? {
              name: initial.name,
              data_scope: initial.data_scope,
              dept_ids: initial.dept_ids,
              description: initial.description ?? undefined,
              status: initial.status,
            }
          : { data_scope: 'self', dept_ids: [] }
      }
      onFinish={(values) => onSubmit(values, permissionIds)}
    >
      {mode === 'create' ? (
        <Form.Item
          name="code"
          label="角色标识"
          rules={[{ required: true, message: '请输入角色标识' }]}
        >
          <Input placeholder="唯一标识，创建后不可改（如 auditor）" />
        </Form.Item>
      ) : (
        <Form.Item label="角色标识">
          <Input value={initial?.code} disabled />
        </Form.Item>
      )}
      <Form.Item name="name" label="角色名称" rules={[{ required: true, message: '请输入角色名称' }]}>
        <Input maxLength={50} placeholder="角色名称" />
      </Form.Item>
      <Form.Item name="data_scope" label="数据范围" rules={[{ required: true }]}>
        <Select options={DATA_SCOPE_OPTIONS} />
      </Form.Item>
      {dataScope === 'custom' && (
        <Form.Item name="dept_ids" label="自定义部门">
          <DeptTreeMultiSelect />
        </Form.Item>
      )}
      <Form.Item name="description" label="描述">
        <Input.TextArea rows={2} maxLength={200} placeholder="描述" />
      </Form.Item>
      {mode === 'edit' && (
        <Form.Item name="status" label="状态">
          <Select options={STATUS_OPTIONS} />
        </Form.Item>
      )}
      <Form.Item label="权限" style={{ marginBottom: 0 }}>
        <PermissionTree value={permissionIds} onChange={setPermissionIds} />
      </Form.Item>
    </Form>
  )
}
