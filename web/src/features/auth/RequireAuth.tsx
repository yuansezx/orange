import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { getToken } from '@shared/auth/token'

/** 路由守卫：无令牌 → 登录页（记下来源，登录后回跳）。 */
export function RequireAuth() {
  const location = useLocation()

  if (getToken() === null) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return <Outlet />
}
