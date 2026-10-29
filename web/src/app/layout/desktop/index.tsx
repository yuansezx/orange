import { Button, Tooltip } from 'antd'
import { useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { usePermission } from '@features/auth'
import type { SystemSidebarState } from '@shared/navigation'
import { DesktopShellFrame } from '@shared/shell'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo } from '@shared/ui'

import {
  filterWorkspacesByPermission,
  workspaceHomePath,
  workspaceOfPath,
  workspaces,
} from '../../routes'
import { SystemSidebar } from '../components/SystemSidebar'

const DEFAULT_STATE: SystemSidebarState = 'expanded'

/** 系统壳 · 桌面：系统侧栏（三态 × push/overlay）+ 内容区。
 *
 * 系统侧栏三态是**系统级**状态（全局一份，切换 workspace / 进入个人中心都不重置），
 * workspace 只能通过 `systemSidebarBehavior` 声明内容挤占或悬浮。
 */
export function DesktopAdminShell() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { can } = usePermission()
  const [systemSidebarState, setSystemSidebarState] =
    useState<SystemSidebarState>(DEFAULT_STATE)

  const allowed = filterWorkspacesByPermission(workspaces, can)
  const current = workspaceOfPath(allowed, pathname)
  const systemSidebarBehavior = current?.systemSidebarBehavior ?? 'push'

  const trigger = (
    <Tooltip title="打开系统导航">
      <Button
        type="text"
        aria-label="打开系统导航"
        onClick={() => setSystemSidebarState('rail')}
        style={{
          width: 40,
          height: 40,
          borderRadius: 8,
          background: colorTokens.bgContainer,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.12)',
        }}
      >
        <BrandLogo size={22} />
      </Button>
    </Tooltip>
  )

  return (
    <DesktopShellFrame
      sidebarState={systemSidebarState}
      sidebarBehavior={systemSidebarBehavior}
      sidebar={
        <SystemSidebar
          workspaces={allowed}
          currentWorkspaceKey={current?.key}
          state={systemSidebarState === 'expanded' ? 'expanded' : 'rail'}
          canHide
          onSelectWorkspace={(workspace) => navigate(workspaceHomePath(workspace))}
          onCollapse={() => setSystemSidebarState('rail')}
          onExpand={() => setSystemSidebarState('expanded')}
          onHide={() => setSystemSidebarState('hidden')}
        />
      }
      trigger={trigger}
    >
      <Outlet />
    </DesktopShellFrame>
  )
}
