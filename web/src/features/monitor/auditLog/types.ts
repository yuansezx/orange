import type { Dayjs } from 'dayjs'

export type AuditResult = 'success' | 'failure'

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
  result?: AuditResult
  range: [Dayjs, Dayjs] | null
}
