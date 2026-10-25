import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'
import { useNavigate } from 'react-router-dom'

import { setToken } from '@shared/auth/token'

import { logout } from '../api/authApi'

/** 登出：服务端吊销令牌 + 清本地令牌与缓存 → 回登录页（成败都清，令牌已无用）。 */
export function useLogout() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { modal } = App.useApp()

  const mutation = useMutation({
    mutationFn: logout,
    onSettled: () => {
      setToken(null)
      queryClient.clear()
      navigate('/login', { replace: true })
    },
  })

  /** 先二次确认再登出——桌面用户菜单与移动端操作表共用，避免误点。 */
  const confirmLogout = () => {
    modal.confirm({
      title: '退出登录？',
      content: '退出后需要重新登录。',
      okText: '退出登录',
      okButtonProps: { danger: true },
      onOk: () => mutation.mutate(),
    })
  }

  return { logout: confirmLogout, loading: mutation.isPending }
}
