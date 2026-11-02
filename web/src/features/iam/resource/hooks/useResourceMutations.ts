import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import type { Status } from '../../types'
import {
  createPermission,
  createResource,
  deletePermission,
  deleteResource,
  hardDeletePermission,
  hardDeleteResource,
  restorePermission,
  restoreResource,
  setPermissionStatus,
  setResourceStatus,
  updatePermission,
  updateResource,
} from '../api/resourceApi'
import type {
  CreatePermissionReq,
  CreateResourceReq,
  UpdatePermissionReq,
  UpdateResourceReq,
} from '../types'

/** 资源 / 权限写操作用例：成功失效列表与权限树目录缓存，失败提示后端 `message`。 */
export function useResourceMutations() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['resources'] })
    queryClient.invalidateQueries({ queryKey: ['permissions'] })
    queryClient.invalidateQueries({ queryKey: ['resource-catalog'] })
  }
  const onError = (error: unknown) =>
    message.error(isApiError(error) ? error.message : '操作失败，请重试')

  const create = useMutation({
    mutationFn: (body: CreateResourceReq) => createResource(body),
    onSuccess: () => {
      message.success('已创建')
      invalidate()
    },
    onError,
  })

  const update = useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateResourceReq }) =>
      updateResource(id, body),
    onSuccess: () => {
      message.success('已保存')
      invalidate()
    },
    onError,
  })

  const setStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Status }) =>
      setResourceStatus(id, status),
    onSuccess: () => {
      message.success('已更新状态')
      invalidate()
    },
    onError,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteResource(id),
    onSuccess: () => {
      message.success('已删除')
      invalidate()
    },
    onError,
  })

  const restore = useMutation({
    mutationFn: (id: string) => restoreResource(id),
    onSuccess: () => {
      message.success('已恢复')
      invalidate()
    },
    onError,
  })

  const hardDelete = useMutation({
    mutationFn: (id: string) => hardDeleteResource(id),
    onSuccess: () => {
      message.success('已彻底删除')
      invalidate()
    },
    onError,
  })

  const createPerm = useMutation({
    mutationFn: (body: CreatePermissionReq) => createPermission(body),
    onSuccess: () => {
      message.success('已创建权限')
      invalidate()
    },
    onError,
  })

  const updatePerm = useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdatePermissionReq }) =>
      updatePermission(id, body),
    onSuccess: () => {
      message.success('已保存')
      invalidate()
    },
    onError,
  })

  const setPermStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Status }) =>
      setPermissionStatus(id, status),
    onSuccess: () => {
      message.success('已更新状态')
      invalidate()
    },
    onError,
  })

  const removePerm = useMutation({
    mutationFn: (id: string) => deletePermission(id),
    onSuccess: () => {
      message.success('已删除')
      invalidate()
    },
    onError,
  })

  const restorePerm = useMutation({
    mutationFn: (id: string) => restorePermission(id),
    onSuccess: () => {
      message.success('已恢复')
      invalidate()
    },
    onError,
  })

  const hardDeletePerm = useMutation({
    mutationFn: (id: string) => hardDeletePermission(id),
    onSuccess: () => {
      message.success('已彻底删除')
      invalidate()
    },
    onError,
  })

  return {
    create,
    update,
    setStatus,
    remove,
    restore,
    hardDelete,
    createPerm,
    updatePerm,
    setPermStatus,
    removePerm,
    restorePerm,
    hardDeletePerm,
  }
}
