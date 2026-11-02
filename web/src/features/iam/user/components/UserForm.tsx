import { Form, Input, Select } from 'antd'

import { DeptTreeSelect } from '../../components/DeptTreeSelect'
import { STATUS_OPTIONS } from '../../constants'
import { useRoles } from '../../role/hooks/useRoles'
import type { UserDetail, UserFormValues } from '../types'

interface Props {
  /** 供抽屉底部的原生 submit 按钮 `form=` 关联。 */
  formId: string
  mode: 'create' | 'edit'
  /** 编辑时先拉详情（含角色），据此初始化。 */
  initial?: UserDetail
  onSubmit: (values: UserFormValues) => void
}

/**
 * 用户表单字段（新建 / 编辑共用，提交由外层抽屉承担）。
 * 由外层以 `key` 重挂，故用 `initialValues` 初始化即可。
 * （只读详情另见 `UserDetailDrawer`，不复用本表单。）
 */
export function UserForm({ formId, mode, initial, onSubmit }: Props) {
  const [form] = Form.useForm<UserFormValues>()
  const { data: roles = [] } = useRoles()
  const roleOptions = roles.map((role) => ({
    value: role.id,
    label: `${role.name}（${role.code}）`,
  }))

  return (
    <Form
      id={formId}
      form={form}
      layout="vertical"
      requiredMark={false}
      initialValues={
        mode === 'edit' && initial
          ? {
              username: initial.username,
              nickname: initial.nickname,
              email: initial.email ?? undefined,
              phone: initial.phone ?? undefined,
              status: initial.status,
              description: initial.description ?? undefined,
              dept_id: initial.dept_id ?? undefined,
              role_ids: initial.roles.map((role) => role.id),
            }
          : { status: 'active', role_ids: [] }
      }
      onFinish={onSubmit}
    >
      {mode === 'create' ? (
        <Form.Item
          name="username"
          label="用户名"
          rules={[{ required: true, whitespace: true, message: '请输入用户名' }]}
        >
          <Input maxLength={50} placeholder="登录名，创建后不可改" />
        </Form.Item>
      ) : (
        <Form.Item label="用户名">
          <Input value={initial?.username} disabled />
        </Form.Item>
      )}
      <Form.Item
        name="nickname"
        label="昵称"
        rules={
          mode === 'edit'
            ? [{ required: true, whitespace: true, message: '请输入昵称' }]
            : undefined
        }
      >
        <Input
          maxLength={50}
          placeholder={mode === 'create' ? '留空则与用户名相同' : '昵称'}
        />
      </Form.Item>
      {mode === 'create' && (
        <Form.Item
          name="password"
          label="初始密码"
          extra="留空则自动生成，首次登录后需修改。"
          rules={[
            {
              validator: (_, value: string | undefined) =>
                !value || value.length >= 8
                  ? Promise.resolve()
                  : Promise.reject(new Error('密码长度不能少于 8 位')),
            },
          ]}
        >
          <Input.Password placeholder="留空自动生成" />
        </Form.Item>
      )}
      <Form.Item name="email" label="邮箱" rules={[{ type: 'email', message: '邮箱格式不正确' }]}>
        <Input placeholder="邮箱" />
      </Form.Item>
      <Form.Item name="phone" label="手机号">
        <Input placeholder="手机号" />
      </Form.Item>
      <Form.Item name="status" label="状态" rules={[{ required: true }]}>
        <Select options={STATUS_OPTIONS} />
      </Form.Item>
      <Form.Item name="dept_id" label="部门">
        <DeptTreeSelect />
      </Form.Item>
      <Form.Item name="role_ids" label="角色">
        <Select
          mode="multiple"
          options={roleOptions}
          placeholder="选择角色"
          optionFilterProp="label"
          showSearch
        />
      </Form.Item>
      <Form.Item name="description" label="描述">
        <Input.TextArea rows={2} maxLength={200} placeholder="描述" />
      </Form.Item>
    </Form>
  )
}
