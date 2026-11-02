import { Button, Checkbox, ErrorBlock, List } from 'antd-mobile'
import { Fragment } from 'react'

import { browserText, formatTime, osText, userLabel } from '../../sessionFormat'
import type { SessionListViewProps } from '../../types'

/**
 * 【分叉档 · 移动】与 desktop/SessionTable 同源：同一份分组数据换卡片形态。
 * 用户行复选框 = 踢其全部会话；会话行复选框 = 踢指定会话。
 */
export function SessionCardList({
  groups,
  loading,
  error,
  canRevokeSessions,
  canRevokeUsers,
  selectedKeys,
  onToggle,
  onRevokeUser,
  onRevokeSession,
}: SessionListViewProps) {
  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  const sessionCount = groups.reduce((sum, group) => sum + group.session_count, 0)

  return (
    <List header={`在线会话（${sessionCount}）`}>
      {groups.map((group) => (
        <Fragment key={group.key}>
          <List.Item
            prefix={
              canRevokeUsers ? (
                <Checkbox
                  checked={selectedKeys.has(group.key)}
                  onChange={(checked) => onToggle(group.key, checked)}
                />
              ) : undefined
            }
            description={`${group.username ? `@${group.username} · ` : ''}${group.session_count} 个会话`}
            extra={
              canRevokeUsers ? (
                <Button size="mini" color="danger" fill="none" onClick={() => onRevokeUser(group)}>
                  全部踢出
                </Button>
              ) : undefined
            }
            style={{ fontWeight: 600 }}
          >
            {userLabel(group)}
          </List.Item>
          {group.children.map((session) => (
            <List.Item
              key={session.key}
              prefix={
                canRevokeSessions ? (
                  <Checkbox
                    checked={selectedKeys.has(session.key)}
                    onChange={(checked) => onToggle(session.key, checked)}
                  />
                ) : undefined
              }
              description={
                <div>
                  <div>{osText(session)}</div>
                  <div>
                    {session.login_ip || '未知 IP'} · 登录 {formatTime(session.login_at)}
                  </div>
                  <div>过期 {formatTime(session.expires_at)}</div>
                </div>
              }
              extra={
                canRevokeSessions ? (
                  <Button size="mini" color="danger" fill="none" onClick={() => onRevokeSession(session)}>
                    踢下线
                  </Button>
                ) : undefined
              }
            >
              {browserText(session)}
            </List.Item>
          ))}
        </Fragment>
      ))}
      {loading && <List.Item>加载中…</List.Item>}
      {!loading && groups.length === 0 && <List.Item>暂无在线会话</List.Item>}
    </List>
  )
}
