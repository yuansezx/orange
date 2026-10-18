import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import type { Status } from '../../types'
import { createDept, deleteDept, setDeptStatus, updateDept } from '../api/deptApi'
import type { CreateDeptReq, UpdateDeptReq } from '../types'

/** 部门写操作用例：成功失效部门树缓存、失败提示后端 `message`。 */
export function useDeptMutations() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['dept-tree'] })
    queryClient.invalidateQueries({ queryKey: ['dept-detail'] })
  }
  const onError = (error: unknown) =>
    message.error(isApiError(error) ? error.message : '操作失败，请重试')

  const create = useMutation({
    mutationFn: (body: CreateDeptReq) => createDept(body),
    onSuccess: () => {
      message.success('已创建')
      invalidate()
    },
    onError,
  })

  const update = useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateDeptReq }) => updateDept(id, body),
    onSuccess: () => {
      message.success('已保存')
      invalidate()
    },
    onError,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteDept(id),
    onSuccess: () => {
      message.success('已删除')
      invalidate()
    },
    onError,
  })

  const setStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Status }) => setDeptStatus(id, status),
    onSuccess: () => {
      message.success('已更新状态')
      invalidate()
    },
    onError,
  })

  return { create, update, remove, setStatus }
}
