import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import { createUser, deleteUser, setUserStatus, updateUser } from '../api/userApi'
import type { CreateUserReq, UpdateUserReq, UserStatus } from '../types'

/** 用户写操作用例：成功失效列表 / 详情 / 下拉目录缓存，失败提示后端 `message`。 */
export function useUserMutations() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['users'] })
    queryClient.invalidateQueries({ queryKey: ['user-detail'] })
    queryClient.invalidateQueries({ queryKey: ['user-directory'] })
  }
  const onError = (error: unknown) =>
    message.error(isApiError(error) ? error.message : '操作失败，请重试')

  const create = useMutation({
    mutationFn: (body: CreateUserReq) => createUser(body),
    onSuccess: () => {
      message.success('已创建')
      invalidate()
    },
    onError,
  })

  const update = useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateUserReq }) => updateUser(id, body),
    onSuccess: () => {
      message.success('已保存')
      invalidate()
    },
    onError,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteUser(id),
    onSuccess: () => {
      message.success('已删除')
      invalidate()
    },
    onError,
  })

  const setStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: UserStatus }) =>
      setUserStatus(id, status),
    onSuccess: () => {
      message.success('已更新状态')
      invalidate()
    },
    onError,
  })

  return { create, update, remove, setStatus }
}
