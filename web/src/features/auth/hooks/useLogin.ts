import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'
import { useLocation, useNavigate } from 'react-router-dom'

import { isApiError } from '@shared/api'
import { setToken } from '@shared/auth/token'

import { login } from '../api/authApi'
import type { LoginReq } from '../types'

/** 登录用例：成功 → 落令牌、清匿名态缓存、回跳（`RequireAuth` 记下的来源，缺省 `/home`）。 */
export function useLogin() {
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const { message } = App.useApp()

  const mutation = useMutation({
    mutationFn: (body: LoginReq) => login(body),
    onSuccess: (data) => {
      setToken(data.access_token)
      queryClient.clear() // 丢弃匿名态下的缓存
      if (data.need_change_password) {
        message.warning('当前为初始密码，请尽快修改')
      }
      const from = (location.state as { from?: string } | null)?.from ?? '/'
      navigate(from, { replace: true })
    },
    onError: (error) => {
      message.error(isApiError(error) ? error.message : '登录失败，请重试')
    },
  })

  return { submit: mutation.mutate, loading: mutation.isPending }
}
