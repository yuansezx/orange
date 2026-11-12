import dayjs from 'dayjs'

import type {
  ApiKey,
  ApiKeyFormValues,
  CreateApiKeyReq,
  UpdateApiKeyReq,
} from './types'

function baseBody(values: ApiKeyFormValues) {
  return {
    name: values.name.trim(),
    scopes: values.scopes,
    data_scope_kind: values.data_scope_kind,
    data_scope_dept_ids:
      values.data_scope_kind === 'custom' ? values.data_scope_dept_ids : [],
  }
}

/** undefined = 省略字段（后端默认 90 天）；null = 永久。 */
function resolveExpiry(values: ApiKeyFormValues): string | null | undefined {
  if (values.expiry_mode === 'default') return undefined
  if (values.expiry_mode === 'never') return null
  return values.expires_at ? values.expires_at.toISOString() : null
}

export function toCreateApiKeyReq(values: ApiKeyFormValues): CreateApiKeyReq {
  const body = baseBody(values)
  const expiresAt = resolveExpiry(values)
  return expiresAt === undefined ? body : { ...body, expires_at: expiresAt }
}

export function toUpdateApiKeyReq(values: ApiKeyFormValues): UpdateApiKeyReq {
  return { ...baseBody(values), expires_at: resolveExpiry(values) ?? null }
}

export const formatTime = (value: string | null) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '—'

export const isExpired = (key: Pick<ApiKey, 'expires_at'>) =>
  key.expires_at !== null && dayjs(key.expires_at).isBefore(dayjs())
