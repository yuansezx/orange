import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'
import { useNavigate } from 'react-router-dom'

import { isApiError } from '@shared/api'
import { setToken } from '@shared/auth/token'

import { changePassword } from '../api/authApi'
import type { ChangePasswordReq } from '../types'

/** 自助改密：服务端已吊销全部会话，成功后清本地态回登录页。 */
export function useChangePassword() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const mutation = useMutation({
    mutationFn: (body: ChangePasswordReq) => changePassword(body),
    onSuccess: () => {
      setToken(null)
      queryClient.clear()
      message.success('密码已修改，请重新登录')
      navigate('/login', { replace: true })
    },
    onError: (error) => {
      message.error(isApiError(error) ? error.message : '修改失败，请重试')
    },
  })

  return { submit: mutation.mutate, loading: mutation.isPending }
}
