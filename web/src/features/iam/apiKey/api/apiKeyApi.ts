import { del, get, post, put } from '@shared/api'

import type {
  ApiKey,
  ApiKeyAdmin,
  ApiKeyCreated,
  CreateApiKeyReq,
  GetAdminApiKeysQuery,
  ScopeCandidate,
  UpdateApiKeyReq,
} from '../types'

const SELF = '/api/iam/users/me/api-keys'
const ADMIN = '/api/iam/api-keys'

export function listMyApiKeys(): Promise<ApiKey[]> {
  return get<ApiKey[]>(SELF)
}

export function getScopeCandidates(): Promise<ScopeCandidate[]> {
  return get<ScopeCandidate[]>(`${SELF}/scope-candidates`)
}

export function createApiKey(body: CreateApiKeyReq): Promise<ApiKeyCreated> {
  return post<ApiKeyCreated>(SELF, body)
}

export function updateApiKey(id: string, body: UpdateApiKeyReq): Promise<ApiKey> {
  return put<ApiKey>(`${SELF}/${id}`, body)
}

export function setMyApiKeyStatus(id: string, status: ApiKey['status']): Promise<ApiKey> {
  return put<ApiKey>(`${SELF}/${id}/status`, { status })
}

/** 吊销 = 软删，不可恢复。 */
export function revokeMyApiKey(id: string): Promise<void> {
  return del<void>(`${SELF}/${id}`)
}

export function listAdminApiKeys(query: GetAdminApiKeysQuery): Promise<ApiKeyAdmin[]> {
  return get<ApiKeyAdmin[]>(ADMIN, query)
}

export function setAdminApiKeyStatus(id: string, status: ApiKey['status']): Promise<ApiKeyAdmin> {
  return put<ApiKeyAdmin>(`${ADMIN}/${id}/status`, { status })
}

export function revokeAdminApiKey(id: string): Promise<void> {
  return del<void>(`${ADMIN}/${id}`)
}
