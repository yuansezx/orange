import { Button, Form, Input, Modal, Select, Space, Tag } from 'antd'
import { useState } from 'react'

import { DeptTreeSelect } from '../../components/DeptTreeSelect'
import { STATUS_OPTIONS } from '../../constants'
import { RolePicker } from '../../role/components/RolePicker'
import type { RoleListItem } from '../../role/types'
import type { UserFormValues, UserListItem } from '../types'

/** 角色字段：按钮打开分页选择弹窗，避免一次拉取全量角色。 */
function RolePickerField({
  value,
  onChange,
}: {
  value?: string[]
  onChange?: (value: string[]) => void
}) {
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState<string[]>([])
  const [labels, setLabels] = useState<Record<string, string>>({})
  const selected = value ?? []

  const rememberLabels = (roles: RoleListItem[]) => {
    if (!roles.length) return
    setLabels((prev) => {
      const next = { ...prev }
      for (const role of roles) next[role.id] = `${role.name}（${role.code}）`
      return next
    })
  }

  return (
    <>
      <Space wrap>
        {selected.map((id) => (
          <Tag
            key={id}
            closable
            onClose={(event) => {
              event.preventDefault()
              onChange?.(selected.filter((roleId) => roleId !== id))
            }}
          >
            {labels[id] ?? id}
          </Tag>
        ))}
        <Button
          onClick={() => {
            setDraft(selected)
            setOpen(true)
          }}
        >
          选择角色
        </Button>
      </Space>
      <Modal
        open={open}
        title="分配角色"
        width={760}
        okText="确定"
        cancelText="取消"
        onOk={() => {
          onChange?.(draft)
          setOpen(false)
        }}
        onCancel={() => setOpen(false)}
      >
        <RolePicker
          value={draft}
          onChange={(ids, roles) => {
            setDraft(ids)
            rememberLabels(roles)
          }}
        />
      </Modal>
    </>
  )
}

interface Props {
  /** 供抽屉底部的原生 submit 按钮 `form=` 关联。 */
  formId: string
  mode: 'create' | 'edit'
  /** 编辑时用列表行初始化（列表已含表单字段；角色走独立管理入口）。 */
  initial?: UserListItem
  /** 创建时是否展示角色字段（`iam:user_role:assign`）；编辑不改角色。 */
  canAssignRoles: boolean
  onSubmit: (values: UserFormValues) => void
}

/**
 * 用户表单字段（新建 / 编辑共用，提交由外层抽屉承担）。
 * 由外层以 `key` 重挂，故用 `initialValues` 初始化即可。
 * （只读详情另见 `UserDetailDrawer`，不复用本表单。）
 */
export function UserForm({ formId, mode, initial, canAssignRoles, onSubmit }: Props) {
  const [form] = Form.useForm<UserFormValues>()

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
            }
          : { status: 'active' }
      }
      onFinish={onSubmit}
    >
      {mode === 'create' ? (
        <Form.Item
          name="username"
          label="用户名"
          rules={[{ required: true, whitespace: true, message: '请输入用户名' }]}
        >
          <Input maxLength={32} placeholder="登录名，创建后不可改" />
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
          maxLength={32}
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
      {mode === 'create' && canAssignRoles && (
        <Form.Item name="role_ids" label="角色">
          <RolePickerField />
        </Form.Item>
      )}
      <Form.Item name="description" label="描述">
        <Input.TextArea rows={2} maxLength={200} placeholder="描述" />
      </Form.Item>
    </Form>
  )
}
