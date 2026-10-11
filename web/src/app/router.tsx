import { Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { LoginPage, RequireAuth } from '@features/auth'
import { PageLoading } from '@shared/ui'

import { AdminShell } from './layout'
import { ADMIN_PATH } from './navigation'
import { NavHome } from './pages/NavHome'
import { menuLinks } from './routes'

/** 路由：登录（壳外）→ 导航页（入口列表）→ 应用壳（后台管理）+ 各菜单页。 */
export function AppRouter() {
  const firstLink = menuLinks[0]?.path

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<RequireAuth />}>
        <Route path="/" element={<NavHome />} />

        <Route path={ADMIN_PATH} element={<AdminShell />}>
          {firstLink && <Route index element={<Navigate to={firstLink} replace />} />}
          {menuLinks.map((link) => (
            <Route
              key={link.key}
              path={link.path}
              element={<Suspense fallback={<PageLoading />}>{link.element}</Suspense>}
            />
          ))}
          {firstLink && <Route path="*" element={<Navigate to={firstLink} replace />} />}
        </Route>
      </Route>
    </Routes>
  )
}
