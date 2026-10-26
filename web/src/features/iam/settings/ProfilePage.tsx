import { Alert, Button, Card, Space, Tag, Typography } from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

import { colorTokens } from '@shared/theme/tokens'
import {
  IconCalendar,
  IconEdit,
  IconKey,
  IconMail,
  IconPhone,
  IconSitemap,
  UserAvatar,
} from '@shared/ui'

import { STATUS_COLORS, STATUS_LABELS } from '../constants'
import { USER_TYPE_LABELS } from '../user/constants'
import { EditProfileModal } from './components/EditProfileModal'
import { useMyProfile } from './hooks/useMyProfile'
import type { MyProfile } from './types'

const formatTime = (value: string | null) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-'

/** 淡色图标底 + 标签/值的信息块。 */
function InfoItem({
  icon,
  label,
  children,
}: {
  icon: ReactNode
  label: string
  children: ReactNode
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, minWidth: 0 }}>
      <div
        style={{
          width: 34,
          height: 34,
          borderRadius: 10,
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: colorTokens.brandSoft,
          color: colorTokens.brandAction,
        }}
      >
        {icon}
      </div>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 12, color: colorTokens.textSecondary, marginBottom: 2 }}>
          {label}
        </div>
        <div style={{ minWidth: 0 }}>{children}</div>
      </div>
    </div>
  )
}

function ProfileHero({
  profile,
  onEdit,
  onSecurity,
}: {
  profile: MyProfile
  onEdit: () => void
  onSecurity: () => void
}) {
  return (
    <Card styles={{ body: { padding: 0 } }}>
      <div
        style={{
          height: 112,
          background: `linear-gradient(120deg, ${colorTokens.brandSoft} 0%, ${colorTokens.bgMuted} 55%, ${colorTokens.bgLayout} 100%)`,
        }}
      />
      <div style={{ padding: '0 24px 24px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-end',
            gap: 16,
            marginTop: -40,
            flexWrap: 'wrap',
          }}
        >
          <div
            style={{
              padding: 4,
              borderRadius: '50%',
              background: colorTokens.bgContainer,
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
            }}
          >
            <UserAvatar name={profile.nickname} size={88} />
          </div>
          <div style={{ flex: 1, minWidth: 200, paddingBottom: 4 }}>
            <Space size={8} wrap style={{ marginBottom: 2 }}>
              <span style={{ fontSize: 22, fontWeight: 700 }}>{profile.nickname}</span>
              <Tag color={STATUS_COLORS[profile.status]}>{STATUS_LABELS[profile.status]}</Tag>
              <Tag>{USER_TYPE_LABELS[profile.user_type]}</Tag>
            </Space>
            <div>
              <Typography.Text type="secondary">@{profile.username}</Typography.Text>
            </div>
          </div>
          <Space size={8} wrap>
            <Button type="primary" icon={<IconEdit size={16} />} onClick={onEdit}>
              修改个人资料
            </Button>
            <Button onClick={onSecurity}>安全设置</Button>
          </Space>
        </div>

        <Space size={8} wrap style={{ marginTop: 16 }}>
          <Typography.Text type="secondary">角色</Typography.Text>
          {profile.roles.length ? (
            profile.roles.map((role) => <Tag key={role.id}>{role.name}</Tag>)
          ) : (
            <Typography.Text type="secondary">未分配</Typography.Text>
          )}
        </Space>
      </div>
    </Card>
  )
}

function ProfileInfo({
  profile,
  onSecurity,
}: {
  profile: MyProfile
  onSecurity: () => void
}) {
  return (
    <Card title="账号信息">
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 20,
        }}
      >
        <InfoItem icon={<IconMail size={16} />} label="邮箱">
          {profile.email ?? <Typography.Text type="secondary">未绑定</Typography.Text>}
        </InfoItem>
        <InfoItem icon={<IconPhone size={16} />} label="手机号">
          {profile.phone ?? <Typography.Text type="secondary">未绑定</Typography.Text>}
        </InfoItem>
        <InfoItem icon={<IconSitemap size={16} />} label="部门">
          {profile.dept?.path ?? <Typography.Text type="secondary">未分配</Typography.Text>}
        </InfoItem>
        <InfoItem icon={<IconCalendar size={16} />} label="创建时间">
          {formatTime(profile.created_at)}
        </InfoItem>
        <InfoItem icon={<IconKey size={16} />} label="密码">
          <Space size={6} wrap>
            <Tag color={profile.need_change_password ? 'warning' : 'success'}>
              {profile.need_change_password ? '待修改' : '已更新'}
            </Tag>
            <Typography.Text type="secondary">
              上次修改 {formatTime(profile.password_updated_at)}
            </Typography.Text>
            <Typography.Link onClick={onSecurity}>修改</Typography.Link>
          </Space>
        </InfoItem>
      </div>

      {profile.description && (
        <div
          style={{
            marginTop: 20,
            paddingTop: 16,
            borderTop: `1px solid ${colorTokens.borderSecondary}`,
          }}
        >
          <div style={{ fontSize: 12, color: colorTokens.textSecondary, marginBottom: 4 }}>
            备注
          </div>
          <div>{profile.description}</div>
        </div>
      )}
    </Card>
  )
}

/** 个人资料：hero + 信息总览；编辑走弹窗。 */
export default function ProfilePage() {
  const { data, isLoading, error } = useMyProfile()
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)

  if (isLoading) return <Card loading style={{ minHeight: 260 }} />
  if (error) return <Alert type="error" message={error.message} showIcon />
  if (!data) return null

  const goSecurity = () => navigate('/account/iam/security')

  return (
    <Space direction="vertical" size={16} style={{ display: 'flex' }}>
      <ProfileHero
        profile={data}
        onEdit={() => setEditing(true)}
        onSecurity={goSecurity}
      />
      <ProfileInfo profile={data} onSecurity={goSecurity} />
      <EditProfileModal
        open={editing}
        profile={data}
        onClose={() => setEditing(false)}
      />
    </Space>
  )
}
