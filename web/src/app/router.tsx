import { Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { PageLoading } from '@shared/ui'

import { AppLayout } from './layout'
import { featureRoutes } from './routes'

/** 聚合各 feature 路由（懒加载），挂在统一的 AppLayout 之下。 */
export function AppRouter() {
  return (
    <Routes>
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
    </Routes>
  )
}
