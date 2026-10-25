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

const DEFAULT_ALLOWED_STATES: SystemNavState[] = ['hidden', 'rail', 'expanded']
const DEFAULT_STATE: SystemNavState = 'expanded'

/** 系统壳 · 桌面：workspace 栏（三态 × push/overlay）+ 内容区。 */
export function DesktopAdminShell() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { can } = usePermission()
  const [stateByWorkspace, setStateByWorkspace] = useState<
    Record<string, SystemNavState>
  >({})

  const allowed = filterWorkspacesByPermission(workspaces, can)
  const current = workspaceOfPath(allowed, pathname)
  const preference = current?.systemNav
  const behavior = preference?.behavior ?? 'push'
  const allowedStates = preference?.allowedStates ?? DEFAULT_ALLOWED_STATES
  const defaultState = preference?.defaultState ?? DEFAULT_STATE
  const navState = (current ? stateByWorkspace[current.key] : undefined) ?? defaultState
  const canHide = allowedStates.includes('hidden')
  const restoreState = allowedStates.find((state) => state !== 'hidden') ?? 'rail'

  const setState = (next: SystemNavState) => {
    if (!current || !allowedStates.includes(next)) return
    setStateByWorkspace((prev) => ({ ...prev, [current.key]: next }))
  }

  const trigger = (
    <Tooltip title="打开系统导航">
      <Button
        type="text"
        aria-label="打开系统导航"
        onClick={() => setState(restoreState)}
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
          canHide={canHide}
          onSelectWorkspace={(workspace) => navigate(workspaceHomePath(workspace))}
          onCollapse={() => setState('rail')}
          onExpand={() => setState('expanded')}
          onHide={() => setState('hidden')}
        />
      }
      trigger={trigger}
    >
      <Outlet />
    </DesktopShellFrame>
  )
}
