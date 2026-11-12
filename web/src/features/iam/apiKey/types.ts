import type { Dayjs } from 'dayjs'

import type { Status } from '../types'

/** API Key 的数据范围（后端只接受 ALL / SELF / CUSTOM）。 */
export type ApiKeyDataScope = 'all' | 'self' | 'custom'

/** 有效期编辑模式：default = 交给后端默认 90 天（仅创建）。 */
export type ExpiryMode = 'default' | 'custom' | 'never'

/** 对齐后端 `ApiKeyResp`（不含明文）。 */
export interface ApiKey {
  id: string
  name: string
  token_masked: string
  scopes: string[]
  data_scope_kind: ApiKeyDataScope
  data_scope_dept_ids: string[]
  status: Status
  expires_at: string | null
  last_used_at: string | null
  created_at: string
  updated_at: string | null
}

/** 对齐后端 `ApiKeyCreatedResp`：明文 token 只出现一次。 */
export interface ApiKeyCreated extends ApiKey {
  token: string
}

/** 列表行（自助/管理共用）：管理端带 `username`。 */
export interface ApiKeyRow extends ApiKey {
  username?: string | null
}

/** 对齐后端 `ApiKeyAdminResp`：附带所属用户。 */
export interface ApiKeyAdmin extends ApiKey {
  user_id: string
  username: string | null
  nickname: string | null
}

export interface ScopeCandidatePermission {
  code: string
  action: string
  name: string
}

/** 对齐后端 `ScopeCandidateResp`：按资源分组的权限候选。 */
export interface ScopeCandidate {
  module: string
  resource: string
  name: string
  permissions: ScopeCandidatePermission[]
}

export interface CreateApiKeyReq {
  name: string
  scopes: string[]
  data_scope_kind: ApiKeyDataScope
  data_scope_dept_ids: string[]
  /** 省略 = 后端默认 90 天；显式 null = 永久。 */
  expires_at?: string | null
}

export interface UpdateApiKeyReq {
  name: string
  scopes: string[]
  data_scope_kind: ApiKeyDataScope
  data_scope_dept_ids: string[]
  /** 显式 null = 永久。 */
  expires_at: string | null
}

export interface GetAdminApiKeysQuery {
  user_id?: string
  status?: Status
  deleted?: boolean
}

/** 表单值：提交前再翻译成 Create/Update 请求。 */
export interface ApiKeyFormValues {
  name: string
  scopes: string[]
  data_scope_kind: ApiKeyDataScope
  data_scope_dept_ids: string[]
  expiry_mode: ExpiryMode
  expires_at: Dayjs | null
}
