/** 在线会话——对齐后端 `SessionResp`。 */
export interface SessionItem {
  user_id: string
  username: string | null
  nickname: string | null
  session_id: string
  login_at: string
  expires_at: string
  login_ip: string | null
  login_user_agent: string | null
  browser: string | null
  browser_version: string | null
  os: string | null
  device: string | null
}

/** 分组表格的会话叶子行。 */
export interface SessionNodeRow extends SessionItem {
  kind: 'session'
  key: string
}

/** 分组表格的用户父行。 */
export interface SessionGroupRow {
  kind: 'user'
  key: string
  user_id: string
  username: string | null
  nickname: string | null
  session_count: number
  children: SessionNodeRow[]
}

export type SessionTableRow = SessionGroupRow | SessionNodeRow

/** 踢出指定会话——按用户分批（后端接口以 user_id 定位 hash）。 */
export interface RevokeSessionsTarget {
  user_id: string
  session_ids: string[]
}

/** 桌面 / 移动视图共用入参；取数与弹层在 SessionPage。 */
export interface SessionListViewProps {
  groups: SessionGroupRow[]
  loading: boolean
  error: Error | null
  canRevokeSessions: boolean
  canRevokeUsers: boolean
  selectedKeys: Set<string>
  onToggle: (key: string, checked: boolean) => void
  onRevokeUser: (group: SessionGroupRow) => void
  onRevokeSession: (session: SessionItem) => void
}
