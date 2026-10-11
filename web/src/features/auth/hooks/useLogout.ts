import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { setToken } from '@shared/auth/token'

import { logout } from '../api/authApi'

/** 登出：服务端吊销令牌 + 清本地令牌与缓存 → 回登录页（成败都清，令牌已无用）。 */
export function useLogout() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: logout,
    onSettled: () => {
      setToken(null)
      queryClient.clear()
      navigate('/login', { replace: true })
    },
  })

  return { logout: mutation.mutate, loading: mutation.isPending }
}
