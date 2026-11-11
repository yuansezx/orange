import type { Dayjs } from 'dayjs'

export type AuditResult = 'success' | 'failure'

/** 单次认证来源（登录事件 password/oauth；业务动作 session/api_key）。 */
export type AuthMethod = 'password' | 'session' | 'api_key' | 'oauth'

export interface AuditLogItem {
  id: string
  occurred_at: string
  module: string
  resource: string
  action: string
  key: string
  summary: string

  target_type: string | null
  target_id: string | null
  target_name: string | null

  operator_id: string | null
  operator_username: string | null
  operator_nickname: string | null

  auth_method: AuthMethod | null
  api_key_id: string | null

  result: AuditResult
  error_code: string | null
  error_message: string | null

  request_id: string | null
  ip: string | null
  user_agent: string | null

  detail: Record<string, unknown>
}

export interface GetAuditLogsQuery {
  page: number
  page_size: number
  module?: string
  resource?: string
  action?: string
  operator_username?: string
  keyword?: string
  auth_method?: AuthMethod
  result?: AuditResult
  occurred_from?: string
  occurred_to?: string
}

export interface AuditLogFilters {
  module: string
  resource: string
  action: string
  operator: string
  keyword: string
  authMethod?: AuthMethod
  result?: AuditResult
  range: [Dayjs, Dayjs] | null
}
