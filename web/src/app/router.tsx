import { Empty } from 'antd'
import { Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { LoginPage, RequireAuth, usePermission } from '@features/auth'
import { PageLoading } from '@shared/ui'

import { AppShell } from './layout'
import { WorkspaceLayout } from './layout/WorkspaceLayout'
import {
  filterWorkspacesByPermission,
  workspaceHomePath,
  type WorkspaceNav,
  workspaces,
} from './routes'
import { SessionExpiryWatcher } from './SessionExpiryWatcher'

/** 无首页：直接落到第一个有权限的 workspace 页面。 */
function RootRedirect() {
  const { can } = usePermission()
  const allowed = filterWorkspacesByPermission(workspaces, can)
  const first = allowed[0]

  if (!first) {
    return <Empty description="暂无可访问模块" style={{ marginTop: 80 }} />
  }
  return <Navigate to={workspaceHomePath(first)} replace />
}

/** workspace 根路径（如 `/admin`）落到该 workspace 的第一个有权限页面。 */
function WorkspaceHomeRedirect({ workspace }: { workspace: WorkspaceNav }) {
  const { can } = usePermission()
  const filtered = filterWorkspacesByPermission([workspace], can)[0]

  if (!filtered) {
    return <Empty description="暂无可访问页面" style={{ marginTop: 80 }} />
  }
  return <Navigate to={workspaceHomePath(filtered)} replace />
}

/** 路由：登录（壳外）→ 系统壳（workspace 栏）→ workspace 内部路由。 */
export function AppRouter() {
  return (
    <>
      {/* 会话失效（401）→ 提示 + 跳登录页 */}
      <SessionExpiryWatcher />

      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<RequireAuth />}>
          <Route element={<AppShell />}>
            <Route index element={<RootRedirect />} />

            {workspaces.map((workspace) => (
              <Route
                key={workspace.key}
                path={workspace.basePath}
                element={<WorkspaceLayout workspace={workspace} />}
              >
                <Route index element={<WorkspaceHomeRedirect workspace={workspace} />} />
                {workspace.features
                  .flatMap((feature) =>
                    feature.groups.flatMap((group) => group.links),
                  )
                  .map((link) => (
                    <Route
                      key={link.key}
                      path={link.featurePath}
                      element={
                        <Suspense fallback={<PageLoading />}>{link.element}</Suspense>
                      }
                    />
                  ))}
              </Route>
            ))}

            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Route>
      </Routes>
    </>
  )
}
