import { ErrorBlock, List } from 'antd-mobile'

import type { UserListViewProps } from '../../types'

/**
 * 【分叉档 · 移动】—— 与 desktop/UserTable 同源：同一份数据，换一种更合手的形态（卡片列表）。
 * 与 UserTable 成对；只负责渲染，取数在 UserPage。
 */
export function UserCardList({ users, loading, error }: UserListViewProps) {
  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }
  return (
    <List header="用户">
      {users.map((user) => (
        <List.Item key={user.id} description={user.username} extra={user.status}>
          {user.nickname || user.username}
        </List.Item>
      ))}
      {loading && <List.Item>加载中…</List.Item>}
    </List>
  )
}
