import { useQuery } from '@tanstack/react-query'
import { Alert, Descriptions, Space, Spin, Tag } from 'antd'

import { auditItems } from '../../components/auditItems'
import { DetailDrawer } from '../../components/DetailDrawer'
import { STATUS_COLORS, STATUS_LABELS } from '../../constants'
import { getUserDetail } from '../api/userApi'
import { USER_TYPE_LABELS } from '../constants'

interface Props {
  open: boolean
  userId?: string
  onClose: () => void
}

/** 用户详情（只读）——进详情时拉 `GET /users/{id}/detail`。 */
export function UserDetailDrawer({ open, userId, onClose }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user-detail', userId],
    queryFn: () => getUserDetail(userId as string),
    enabled: open && !!userId,
  })

  return (
    <DetailDrawer
      open={open}
      title={data ? `用户详情 · ${data.username}` : '用户详情'}
      onClose={onClose}
    >
      {isLoading ? (
        <Spin />
      ) : error ? (
        <Alert type="error" showIcon message={error.message} />
      ) : data ? (
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="用户名">{data.username}</Descriptions.Item>
          <Descriptions.Item label="昵称">{data.nickname}</Descriptions.Item>
          <Descriptions.Item label="类型">{USER_TYPE_LABELS[data.user_type]}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={STATUS_COLORS[data.status]}>{STATUS_LABELS[data.status]}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="部门">{data.dept_ref?.path ?? '-'}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{data.email || '-'}</Descriptions.Item>
          <Descriptions.Item label="手机号">{data.phone || '-'}</Descriptions.Item>
          <Descriptions.Item label="角色">
            {data.roles.length > 0 ? (
              <Space size={[4, 4]} wrap>
                {data.roles.map((role) => (
                  <Tag key={role.id}>
                    {role.name}（{role.code}）
                  </Tag>
                ))}
              </Space>
            ) : (
              '-'
            )}
          </Descriptions.Item>
          <Descriptions.Item label="描述">{data.description || '-'}</Descriptions.Item>
          {auditItems(data)}
        </Descriptions>
      ) : null}
    </DetailDrawer>
  )
}
