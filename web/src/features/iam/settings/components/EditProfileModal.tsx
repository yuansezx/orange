import { Form, Input, Modal, Typography } from 'antd'
import { useEffect } from 'react'

import { IconMail, IconPhone, IconUserCircle } from '@shared/ui'

import { useUpdateMyProfile } from '../hooks/useMyProfile'
import type { MyProfile } from '../types'

interface FormValues {
  nickname: string
  email?: string
  phone?: string
}

interface Props {
  open: boolean
  profile: MyProfile
  onClose: () => void
}

/** 修改个人资料：只允许昵称 / 邮箱 / 手机号。 */
export function EditProfileModal({ open, profile, onClose }: Props) {
  const [form] = Form.useForm<FormValues>()
  const update = useUpdateMyProfile()

  useEffect(() => {
    if (!open) return
    form.setFieldsValue({
      nickname: profile.nickname,
      email: profile.email ?? undefined,
      phone: profile.phone ?? undefined,
    })
  }, [open, profile, form])

  const submit = (values: FormValues) =>
    update.mutate(
      {
        nickname: values.nickname.trim(),
        email: values.email?.trim() || null,
        phone: values.phone?.trim() || null,
      },
      { onSuccess: onClose },
    )

  return (
    <Modal
      open={open}
      title="修改个人资料"
      okText="保存"
      cancelText="取消"
      confirmLoading={update.isPending}
      onOk={() => form.submit()}
      onCancel={() => {
        if (!update.isPending) onClose()
      }}
    >
      <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
        邮箱、手机号留空表示不绑定。
      </Typography.Paragraph>

      <Form form={form} layout="vertical" requiredMark={false} onFinish={submit}>
        <Form.Item
          name="nickname"
          label="昵称"
          rules={[
            { required: true, whitespace: true, message: '请输入昵称' },
            { max: 64, message: '昵称不能超过 64 个字符' },
          ]}
        >
          <Input prefix={<IconUserCircle size={16} />} maxLength={64} placeholder="请输入昵称" />
        </Form.Item>

        <Form.Item
          name="email"
          label="邮箱"
          rules={[{ type: 'email', message: '邮箱格式不正确' }]}
        >
          <Input prefix={<IconMail size={16} />} maxLength={255} placeholder="不绑定可留空" />
        </Form.Item>

        <Form.Item
          name="phone"
          label="手机号"
          rules={[
            {
              validator: (_, value: string | undefined) =>
                !value || /^1[3-9]\d{9}$/.test(value.trim())
                  ? Promise.resolve()
                  : Promise.reject(new Error('手机号格式不正确')),
            },
          ]}
        >
          <Input prefix={<IconPhone size={16} />} maxLength={20} placeholder="不绑定可留空" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
