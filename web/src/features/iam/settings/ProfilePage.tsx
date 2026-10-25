import { Alert, Card, Descriptions, Typography } from 'antd'

import { useMe } from '@features/auth'
import { UserAvatar } from '@shared/ui'

import { USER_TYPE_LABELS } from '../user/constants'

/** 个人资料（框架版）：先用 `/me` 快照，邮箱/手机号等接口待后端接入。 */
export default function ProfilePage() {
  const { data: me, isLoading } = useMe()

  return (
    <Card loading={isLoading}>
      {me && (
        <>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              marginBottom: 20,
            }}
          >
            <UserAvatar name={me.nickname} src={me.avatar} size={64} />
            <div>
              <div style={{ fontSize: 18, fontWeight: 600 }}>{me.nickname}</div>
              <Typography.Text type="secondary">@{me.username}</Typography.Text>
            </div>
          </div>

          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="用户名">{me.username}</Descriptions.Item>
            <Descriptions.Item label="昵称">{me.nickname}</Descriptions.Item>
            <Descriptions.Item label="用户类型">
              {USER_TYPE_LABELS[me.user_type]}
            </Descriptions.Item>
            <Descriptions.Item label="角色">
              {me.roles?.length ? me.roles.map((role) => role.name).join('、') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="部门">{me.dept_id ?? '-'}</Descriptions.Item>
          </Descriptions>

          <Alert
            style={{ marginTop: 16 }}
            type="info"
            showIcon
            message="邮箱、手机号、头像等资料接口待后端接入"
          />
        </>
      )}
    </Card>
  )
}
