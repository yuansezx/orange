import type { AuditResult, AuthMethod } from './types'

export const RESULT_LABELS: Record<AuditResult, string> = {
  success: '成功',
  failure: '失败',
}

export const AUTH_METHOD_LABELS: Record<AuthMethod, string> = {
  password: '密码登录',
  session: '会话',
  api_key: 'API Key',
  oauth: 'OAuth',
}

export const AUTH_METHOD_COLORS: Record<AuthMethod, string> = {
  password: 'blue',
  session: 'default',
  api_key: 'purple',
  oauth: 'cyan',
}
