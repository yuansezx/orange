import { Button, Space } from 'antd'

import { IconLogout, IconRefresh, IconUserX } from '@shared/ui'

interface Props {
  refreshing: boolean
  canRevokeSessions: boolean
  canRevokeUsers: boolean
  selectedSessionCount: number
  selectedUserCount: number
  revokingSessions: boolean
  revokingUsers: boolean
  onRefresh: () => void
  onRevokeSelectedSessions: () => void
  onRevokeSelectedUsers: () => void
}

/** 在线会话工具栏：刷新 + 两类批量踢下线（两端共用）。 */
export function SessionToolbar({
  refreshing,
  canRevokeSessions,
  canRevokeUsers,
  selectedSessionCount,
  selectedUserCount,
  revokingSessions,
  revokingUsers,
  onRefresh,
  onRevokeSelectedSessions,
  onRevokeSelectedUsers,
}: Props) {
  return (
    <Space style={{ display: 'flex', marginBottom: 16, flexWrap: 'wrap' }} size={12}>
      <Button icon={<IconRefresh size={16} />} loading={refreshing} onClick={onRefresh}>
        刷新
      </Button>
      {canRevokeSessions && (
        <Button
          danger
          icon={<IconLogout size={16} />}
          disabled={selectedSessionCount === 0}
          loading={revokingSessions}
          onClick={onRevokeSelectedSessions}
        >
          踢出选中会话{selectedSessionCount > 0 ? `（${selectedSessionCount}）` : ''}
        </Button>
      )}
      {canRevokeUsers && (
        <Button
          danger
          icon={<IconUserX size={16} />}
          disabled={selectedUserCount === 0}
          loading={revokingUsers}
          onClick={onRevokeSelectedUsers}
        >
          踢出选中用户{selectedUserCount > 0 ? `（${selectedUserCount}）` : ''}
        </Button>
      )}
    </Space>
  )
}
