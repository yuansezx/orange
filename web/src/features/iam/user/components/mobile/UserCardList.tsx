import { ActionSheet, ErrorBlock, List } from 'antd-mobile'
import dayjs from 'dayjs'
import { useState } from 'react'

import { STATUS_LABELS, USER_TYPE_LABELS } from '../../constants'
import type { UserListItem, UserListViewProps } from '../../types'

/**
 * 【分叉档 · 移动】—— 与 desktop/UserTable 同源：同一份数据，换一种更合手的形态（卡片列表）。
 * 点项弹 ActionSheet 出操作（查看/编辑/删除）。
 */
export function UserCardList({
  users,
  loading,
  error,
  recycleMode,
  onView,
  onEdit,
  onDelete,
  onRestore,
  onHardDelete,
}: UserListViewProps) {
  const [active, setActive] = useState<UserListItem | null>(null)

  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <>
      <List header="用户">
        {users.map((user) => (
          <List.Item
            key={user.id}
            onClick={() => setActive(user)}
            description={`${user.username} · ${USER_TYPE_LABELS[user.user_type]} · ${dayjs(
              user.created_at,
            ).format('YYYY-MM-DD')}`}
            extra={STATUS_LABELS[user.status]}
          >
            {user.nickname || user.username}
          </List.Item>
        ))}
        {loading && <List.Item>加载中…</List.Item>}
        {!loading && users.length === 0 && <List.Item>暂无用户</List.Item>}
      </List>

      <ActionSheet
        visible={active !== null}
        cancelText="取消"
        onClose={() => setActive(null)}
        actions={
          recycleMode
            ? [
                { key: 'view', text: '查看' },
                { key: 'restore', text: '恢复' },
                { key: 'hardDelete', text: '彻底删除', danger: true },
              ]
            : [
                { key: 'view', text: '查看' },
                { key: 'edit', text: '编辑' },
                { key: 'delete', text: '删除', danger: true },
              ]
        }
        onAction={(action) => {
          if (!active) return
          const target = active
          setActive(null)
          if (action.key === 'view') onView(target)
          else if (action.key === 'restore') onRestore(target)
          else if (action.key === 'hardDelete') onHardDelete(target)
          else if (action.key === 'edit') onEdit(target)
          else if (action.key === 'delete') onDelete(target)
        }}
      />
    </>
  )
}
