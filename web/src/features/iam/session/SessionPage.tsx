import { App } from 'antd'
import { useMemo, useState } from 'react'

import { usePermission } from '@features/auth'
import { Platform } from '@shared/platform'

import { SessionToolbar } from './components/SessionToolbar'
import { SessionTable } from './components/desktop/SessionTable'
import { SessionCardList } from './components/mobile/SessionCardList'
import { useSessionMutations } from './hooks/useSessionMutations'
import { useSessions } from './hooks/useSessions'
import { groupSessions, resolveSelection, toRevokeTargets } from './sessionFormat'
import type { SessionGroupRow, SessionItem } from './types'

/**
 * 在线会话页：取数一份，工具栏两端共用；
 * 列表形态桌面（分组表格）/ 移动（卡片）分叉。
 */
export default function SessionPage() {
  const { data, isLoading, isFetching, error, refetch } = useSessions()
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set())
  const { can } = usePermission()
  const { modal } = App.useApp()
  const { revokeSessions, revokeUsers } = useSessionMutations()

  const groups = useMemo(() => groupSessions(data ?? []), [data])
  const selection = useMemo(() => resolveSelection(groups, selectedKeys), [groups, selectedKeys])

  const canRevokeSessions = can('iam:current_user:revoke_sessions')
  const canRevokeUsers = can('iam:current_user:revoke_users')

  const toggle = (key: string, checked: boolean) =>
    setSelectedKeys((prev) => {
      const next = new Set(prev)
      if (checked) next.add(key)
      else next.delete(key)
      return next
    })

  const clearSelection = () => setSelectedKeys(new Set())

  const confirmRevokeSessions = (sessions: SessionItem[]) => {
    if (!sessions.length) return
    modal.confirm({
      title: sessions.length === 1 ? '踢出该会话？' : `踢出选中的 ${sessions.length} 个会话？`,
      content: '被踢出的设备需要重新登录。',
      okText: '踢下线',
      okButtonProps: { danger: true },
      onOk: async () => {
        await revokeSessions.mutateAsync(toRevokeTargets(sessions))
        clearSelection()
      },
    })
  }

  const confirmRevokeUsers = (userIds: string[]) => {
    if (!userIds.length) return
    modal.confirm({
      title:
        userIds.length === 1
          ? '踢出该用户的全部会话？'
          : `踢出选中的 ${userIds.length} 个用户的全部会话？`,
      content: '相关设备需要重新登录。',
      okText: '全部踢出',
      okButtonProps: { danger: true },
      onOk: async () => {
        await revokeUsers.mutateAsync(userIds)
        clearSelection()
      },
    })
  }

  const viewProps = {
    groups,
    loading: isLoading,
    error,
    canRevokeSessions,
    canRevokeUsers,
    selectedKeys,
    onToggle: toggle,
    onRevokeUser: (group: SessionGroupRow) => confirmRevokeUsers([group.user_id]),
    onRevokeSession: (session: SessionItem) => confirmRevokeSessions([session]),
  }

  return (
    <div>
      <SessionToolbar
        refreshing={isFetching}
        canRevokeSessions={canRevokeSessions}
        canRevokeUsers={canRevokeUsers}
        selectedSessionCount={selection.sessions.length}
        selectedUserCount={selection.userIds.length}
        revokingSessions={revokeSessions.isPending}
        revokingUsers={revokeUsers.isPending}
        onRefresh={() => void refetch()}
        onRevokeSelectedSessions={() => confirmRevokeSessions(selection.sessions)}
        onRevokeSelectedUsers={() => confirmRevokeUsers(selection.userIds)}
      />
      <Platform
        desktop={
          <SessionTable
            {...viewProps}
            onSelectionChange={(keys) => setSelectedKeys(new Set(keys))}
          />
        }
        mobile={<SessionCardList {...viewProps} />}
      />
    </div>
  )
}
