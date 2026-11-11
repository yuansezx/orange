import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import {
  createApiKey,
  revokeAdminApiKey,
  revokeMyApiKey,
  setAdminApiKeyStatus,
  setMyApiKeyStatus,
  updateApiKey,
} from '../api/apiKeyApi'
import type { ApiKey, CreateApiKeyReq, UpdateApiKeyReq } from '../types'

/** API Key 写操作：成功失效自助/管理列表，失败提示后端 `message`。 */
export function useApiKeyMutations() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const invalidateLists = () => {
    queryClient.invalidateQueries({ queryKey: ['me', 'api-keys'] })
    queryClient.invalidateQueries({ queryKey: ['admin', 'api-keys'] })
  }
  const onError = (error: unknown) =>
    message.error(isApiError(error) ? error.message : '操作失败，请重试')

  const create = useMutation({
    mutationFn: (body: CreateApiKeyReq) => createApiKey(body),
    onSuccess: () => {
      message.success('已创建')
      invalidateLists()
    },
    onError,
  })

  const update = useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateApiKeyReq }) => updateApiKey(id, body),
    onSuccess: () => {
      message.success('已保存')
      invalidateLists()
    },
    onError,
  })

  const setStatus = useMutation({
    mutationFn: ({ id, status, admin }: { id: string; status: ApiKey['status']; admin?: boolean }) =>
      admin ? setAdminApiKeyStatus(id, status) : setMyApiKeyStatus(id, status),
    onSuccess: () => {
      message.success('已更新状态')
      invalidateLists()
    },
    onError,
  })

  const revoke = useMutation({
    mutationFn: ({ id, admin }: { id: string; admin?: boolean }) =>
      admin ? revokeAdminApiKey(id) : revokeMyApiKey(id),
    onSuccess: () => {
      message.success('已吊销')
      invalidateLists()
    },
    onError,
  })

  return { create, update, setStatus, revoke }
}
