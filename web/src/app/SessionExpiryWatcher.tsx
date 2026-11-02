import { App } from 'antd'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import { onSessionExpired } from '@shared/auth/session'

/**
 * 订阅「会话失效（401）」：提示 + 跳登录页。
 * 须挂在 Router 内（依赖 `useNavigate` 与 antd 上下文）。
 */
export function SessionExpiryWatcher() {
  const navigate = useNavigate()
  const { message } = App.useApp()

  useEffect(
    () =>
      onSessionExpired(() => {
        message.warning('登录已过期，请重新登录')
        navigate('/login', { replace: true })
      }),
    [navigate, message],
  )

  return null
}
