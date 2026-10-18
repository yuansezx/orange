import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import type { Status } from '../../types'
import { createRole, deleteRole, setRoleStatus, updateRole } from '../api/roleApi'
import type { CreateRoleReq, UpdateRoleReq } from '../types'

/** 角色写操作用例：成功失效角色列表缓存、失败提示后端 `message`。 */
export function useRoleMutations() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['roles'] })
    queryClient.invalidateQueries({ queryKey: ['role-detail'] })
  }
  const onError = (error: unknown) =>
    message.error(isApiError(error) ? error.message : '操作失败，请重试')

  const create = useMutation({
    mutationFn: (body: CreateRoleReq) => createRole(body),
    onSuccess: () => {
      message.success('已创建')
      invalidate()
    },
    onError,
  })

  const update = useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateRoleReq }) => updateRole(id, body),
    onSuccess: () => {
      message.success('已保存')
      invalidate()
    },
    onError,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteRole(id),
    onSuccess: () => {
      message.success('已删除')
      invalidate()
    },
    onError,
  })

  const setStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Status }) => setRoleStatus(id, status),
    onSuccess: () => {
      message.success('已更新状态')
      invalidate()
    },
    onError,
  })

  return { create, update, remove, setStatus }
}
