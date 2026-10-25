import dayjs from 'dayjs'

import type {
  RevokeSessionsTarget,
  SessionGroupRow,
  SessionItem,
  SessionNodeRow,
} from './types'

/** 扁平会话列表 → 按用户分组的树（后端已按 login_at 倒序）。 */
export function groupSessions(sessions: SessionItem[]): SessionGroupRow[] {
  const map = new Map<string, SessionGroupRow>()
  for (const session of sessions) {
    let group = map.get(session.user_id)
    if (!group) {
      group = {
        kind: 'user',
        key: `user:${session.user_id}`,
        user_id: session.user_id,
        username: session.username,
        nickname: session.nickname,
        session_count: 0,
        children: [],
      }
      map.set(session.user_id, group)
    }
    const row: SessionNodeRow = { ...session, kind: 'session', key: `session:${session.session_id}` }
    group.children.push(row)
    group.session_count += 1
  }
  return [...map.values()]
}

/** 勾选状态 → 用户级 / 会话级两类目标（父行选中时不再重复算其子会话）。 */
export function resolveSelection(
  groups: SessionGroupRow[],
  keys: Set<string>,
): { userIds: string[]; sessions: SessionItem[] } {
  const userIds: string[] = []
  const sessions: SessionItem[] = []
  for (const group of groups) {
    if (keys.has(group.key)) {
      userIds.push(group.user_id)
      continue
    }
    for (const row of group.children) {
      if (keys.has(row.key)) sessions.push(row)
    }
  }
  return { userIds, sessions }
}

/** 会话按用户分批，供 `DELETE /sessions/{user_id}` 逐用户调用。 */
export function toRevokeTargets(sessions: SessionItem[]): RevokeSessionsTarget[] {
  const map = new Map<string, string[]>()
  for (const session of sessions) {
    const ids = map.get(session.user_id) ?? []
    ids.push(session.session_id)
    map.set(session.user_id, ids)
  }
  return [...map].map(([user_id, session_ids]) => ({ user_id, session_ids }))
}

export function userLabel(group: SessionGroupRow): string {
  return group.nickname || group.username || group.user_id
}

export function browserText(session: SessionItem): string {
  if (!session.browser) return '未知浏览器'
  return session.browser_version ? `${session.browser} ${session.browser_version}` : session.browser
}

export function osText(session: SessionItem): string {
  return [session.os, session.device].filter(Boolean).join(' · ') || '未知系统'
}

export function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm:ss')
}
