import {
  Alert,
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  Space,
  Tag,
  Typography,
} from 'antd'
import dayjs from 'dayjs'
import { useEffect } from 'react'

import { UserAvatar } from '@shared/ui'

import { STATUS_COLORS, STATUS_LABELS } from '../constants'
import { USER_TYPE_LABELS } from '../user/constants'
import { useMyProfile, useUpdateMyProfile } from './hooks/useMyProfile'
import type { MyProfile } from './types'

interface ProfileFormValues {
  nickname: string
  email?: string
  phone?: string
}

const formatTime = (value: string | null) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-'

function ProfileSummary({ profile }: { profile: MyProfile }) {
  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
        <UserAvatar name={profile.nickname} size={64} />
        <div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>{profile.nickname}</div>
          <Typography.Text type="secondary">@{profile.username}</Typography.Text>
        </div>
      </div>

      <Descriptions column={1} bordered size="small">
        <Descriptions.Item label="邮箱">{profile.email ?? '-'}</Descriptions.Item>
        <Descriptions.Item label="手机号">{profile.phone ?? '-'}</Descriptions.Item>
        <Descriptions.Item label="用户类型">
          {USER_TYPE_LABELS[profile.user_type]}
        </Descriptions.Item>
        <Descriptions.Item label="状态">
          <Tag color={STATUS_COLORS[profile.status]}>{STATUS_LABELS[profile.status]}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="部门">{profile.dept?.path ?? '-'}</Descriptions.Item>
        <Descriptions.Item label="角色">
          {profile.roles.length
            ? profile.roles.map((role) => <Tag key={role.id}>{role.name}</Tag>)
            : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="密码">
          {profile.need_change_password ? (
            <Tag color="warning">待修改</Tag>
          ) : (
            <Tag color="success">已更新</Tag>
          )}
          <Typography.Text type="secondary">
            上次修改：{formatTime(profile.password_updated_at)}
          </Typography.Text>
        </Descriptions.Item>
        <Descriptions.Item label="创建时间">{formatTime(profile.created_at)}</Descriptions.Item>
        {profile.description && (
          <Descriptions.Item label="备注">{profile.description}</Descriptions.Item>
        )}
      </Descriptions>
    </>
  )
}

/** 个人资料：自助读取 + 编辑昵称 / 邮箱 / 手机号。 */
export default function ProfilePage() {
  const { data, isLoading, error } = useMyProfile()
  const update = useUpdateMyProfile()
  const [form] = Form.useForm<ProfileFormValues>()

  useEffect(() => {
    if (!data) return
    form.setFieldsValue({
      nickname: data.nickname,
      email: data.email ?? undefined,
      phone: data.phone ?? undefined,
    })
  }, [data, form])

  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const submit = (values: ProfileFormValues) =>
    update.mutate({
      nickname: values.nickname.trim(),
      email: values.email?.trim() || null,
      phone: values.phone?.trim() || null,
    })

  return (
    <Space direction="vertical" size={16} style={{ display: 'flex' }}>
      <Card loading={isLoading}>{data && <ProfileSummary profile={data} />}</Card>

      <Card title="编辑资料" loading={isLoading}>
        <Form
          form={form}
          layout="vertical"
          requiredMark={false}
          onFinish={submit}
          style={{ maxWidth: 480 }}
        >
          <Form.Item
            name="nickname"
            label="昵称"
            rules={[
              { required: true, whitespace: true, message: '请输入昵称' },
              { max: 64, message: '昵称不能超过 64 个字符' },
            ]}
          >
            <Input maxLength={64} placeholder="请输入昵称" />
          </Form.Item>

          <Form.Item
            name="email"
            label="邮箱"
            rules={[{ type: 'email', message: '邮箱格式不正确' }]}
          >
            <Input maxLength={255} placeholder="留空表示不绑定" />
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
            <Input maxLength={20} placeholder="留空表示不绑定" />
          </Form.Item>

          <Button type="primary" htmlType="submit" loading={update.isPending}>
            保存
          </Button>
        </Form>
      </Card>
    </Space>
  )
}
