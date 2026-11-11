import type { ApiKeyDataScope } from './types'

export const API_KEY_DATA_SCOPE_LABELS: Record<ApiKeyDataScope, string> = {
  all: '全部数据',
  self: '仅本人',
  custom: '自定义部门',
}
