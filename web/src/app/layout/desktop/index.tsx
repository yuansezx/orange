import { Button, Tooltip } from 'antd'
import { useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { usePermission } from '@features/auth'
import type { SystemNavState } from '@shared/navigation'
import { DesktopShellFrame } from '@shared/shell'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo } from '@shared/ui'

import {
  filterWorkspacesByPermission,
  workspaceHomePath,
  workspaceOfPath,
  workspaces,
} from '../../routes'
import { SystemNav } from '../components/SystemNav'

const DEFAULT_STATE: SystemNavState = 'expanded'

/** 系统壳 · 桌面：workspace 栏（三态 × push/overlay）+ 内容区。
 *
 * 系统栏三态是**系统级**状态（全局一份，切换 workspace / 进入个人中心都不重置），
 * workspace 只能通过 `navBehavior` 声明内容挤占或悬浮。
 */
export function DesktopAdminShell() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { can } = usePermission()
  const [navState, setNavState] = useState<SystemNavState>(DEFAULT_STATE)

  const allowed = filterWorkspacesByPermission(workspaces, can)
  const current = workspaceOfPath(allowed, pathname)
  const behavior = current?.navBehavior ?? 'push'

  const trigger = (
    <Tooltip title="打开系统导航">
      <Button
        type="text"
        aria-label="打开系统导航"
        onClick={() => setNavState('rail')}
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
      navState={navState}
      navBehavior={behavior}
      nav={
        <SystemNav
          workspaces={allowed}
          currentWorkspaceKey={current?.key}
          state={navState === 'expanded' ? 'expanded' : 'rail'}
          canHide
          onSelectWorkspace={(workspace) => navigate(workspaceHomePath(workspace))}
          onCollapse={() => setNavState('rail')}
          onExpand={() => setNavState('expanded')}
          onHide={() => setNavState('hidden')}
        />
      }
      trigger={trigger}
    >
      <Outlet />
    </DesktopShellFrame>
  )
}
