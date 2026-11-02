import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import { getMySessions, revokeMySessions } from '../api/sessionsApi'

export function useMySessions() {
  return useQuery({
    queryKey: ['me', 'sessions'],
    queryFn: getMySessions,
  })
}

export function useRevokeMySessions() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  return useMutation({
    mutationFn: (sessionIds: string[]) => revokeMySessions(sessionIds),
    onSuccess: () => message.success('已退出所选设备'),
    onError: (error) =>
      message.error(isApiError(error) ? error.message : '操作失败，请重试'),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: ['me', 'sessions'] }),
  })
}
