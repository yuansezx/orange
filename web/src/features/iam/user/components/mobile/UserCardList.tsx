import { ErrorBlock, List } from 'antd-mobile'
import dayjs from 'dayjs'

import { STATUS_LABELS, USER_TYPE_LABELS } from '../../constants'
import type { UserListViewProps } from '../../types'

/**
 * 【分叉档 · 移动】—— 与 desktop/UserTable 同源：同一份数据，换一种更合手的形态（卡片列表）。
 * 与 UserTable 成对；只负责渲染，取数在 UserPage。
 */
export function UserCardList({ users, loading, error, onView }: UserListViewProps) {
  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }
  return (
    <List header="用户">
      {users.map((user) => (
        <List.Item
          key={user.id}
          onClick={() => onView(user)}
          arrow
          description={`${user.username} · ${USER_TYPE_LABELS[user.user_type]} · ${dayjs(
            user.created_at,
          ).format('YYYY-MM-DD')}`}
          extra={STATUS_LABELS[user.status]}
        >
          {user.nickname || user.username}
        </List.Item>
      ))}
      {loading && <List.Item>加载中…</List.Item>}
    </List>
  )
}
