import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import { revokeUserSessions, revokeUsers as revokeUsersApi } from '../api/sessionApi'
import type { RevokeSessionsTarget } from '../types'

/** 踢下线写操作：成功后失效会话列表，失败提示后端 `message`。 */
export function useSessionMutations() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['sessions'] })
  const onError = (error: unknown) =>
    message.error(isApiError(error) ? error.message : '操作失败，请重试')

  const revokeSessions = useMutation({
    mutationFn: (targets: RevokeSessionsTarget[]) =>
      Promise.all(targets.map(({ user_id, session_ids }) => revokeUserSessions(user_id, session_ids))),
    onSuccess: () => message.success('已踢下线'),
    onError,
    onSettled: invalidate,
  })

  const revokeUsers = useMutation({
    mutationFn: (userIds: string[]) => revokeUsersApi(userIds),
    onSuccess: () => message.success('已踢下线'),
    onError,
    onSettled: invalidate,
  })

  return { revokeSessions, revokeUsers }
}
