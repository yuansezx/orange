import { Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { LoginPage, RequireAuth } from '@features/auth'
import { PageLoading } from '@shared/ui'

import { AppLayout } from './layout'
import { featureRoutes } from './routes'

/** 聚合：登录页（壳外） + 受保护的应用壳（壳内各 feature 路由懒加载）。 */
export function AppRouter() {
  return (
    <Routes>
      {/* 登录页在应用壳之外，不受守卫约束 */}
      <Route path="/login" element={<LoginPage />} />

      {/* 其余全部需登录 */}
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/home" replace />} />
          {featureRoutes.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={<Suspense fallback={<PageLoading />}>{route.element}</Suspense>}
            />
          ))}
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Route>
      </Route>
    </Routes>
  )
}
