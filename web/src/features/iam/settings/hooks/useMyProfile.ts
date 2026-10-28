import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import {
  deleteMyAvatar,
  getMyProfile,
  updateMyProfile,
  uploadMyAvatar,
} from '../api/profileApi'
import type { UpdateMyProfileReq } from '../types'

export function useMyProfile() {
  return useQuery({
    queryKey: ['me', 'profile'],
    queryFn: getMyProfile,
  })
}

export function useUpdateMyProfile() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  return useMutation({
    mutationFn: (body: UpdateMyProfileReq) => updateMyProfile(body),
    onSuccess: () => message.success('资料已更新'),
    onError: (error) =>
      message.error(isApiError(error) ? error.message : '保存失败，请重试'),
    // 昵称也在 /me 快照里：失效 ['me'] 同时刷新用户菜单与资料
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['me'] }),
  })
}

export function useUploadMyAvatar() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  return useMutation({
    mutationFn: (file: File) => uploadMyAvatar(file),
    onSuccess: () => message.success('头像已更新'),
    onError: (error) =>
      message.error(isApiError(error) ? error.message : '上传失败，请重试'),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['me'] }),
  })
}

export function useDeleteMyAvatar() {
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  return useMutation({
    mutationFn: deleteMyAvatar,
    onSuccess: () => message.success('头像已删除'),
    onError: (error) =>
      message.error(isApiError(error) ? error.message : '删除失败，请重试'),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['me'] }),
  })
}
