import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import { createDept, deleteDept, updateDept } from '../api/deptApi'
import type { CreateDeptReq, UpdateDeptReq } from '../types'

/** 部门写操作用例：成功失效部门树缓存、失败提示后端 `message`。 */
export function useDeptMutations() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['dept-tree'] })
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

  return { create, update, remove }
}
