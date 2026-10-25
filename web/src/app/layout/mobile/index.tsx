import { ActionSheet, List, Popup } from 'antd-mobile'
import { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { useLogout, usePermission } from '@features/auth'
import { appConfig } from '@shared/config'
import { MobileShellFrame } from '@shared/shell'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo, IconBox, UserAvatar } from '@shared/ui'

import {
  filterWorkspacesByPermission,
  workspaceHomePath,
  workspaceOfPath,
  workspaces,
} from '../../routes'

/** 汉堡菜单图标（三横）——内联 SVG，零依赖。 */
function MenuIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden
    >
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  )
}

/** 更多设置图标（三个竖点）。 */
function MoreIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <circle cx="12" cy="5" r="2" />
      <circle cx="12" cy="12" r="2" />
      <circle cx="12" cy="19" r="2" />
    </svg>
  )
}

const iconButton = {
  width: 40,
  height: 40,
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  border: 'none',
  background: 'none',
  color: colorTokens.brand,
  cursor: 'pointer',
} as const

/** 系统壳 · 移动：顶栏 + 内容 + workspace 抽屉。 */
export function MobileAdminShell() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { can, me } = usePermission()
  const { logout } = useLogout()
  const [menuOpen, setMenuOpen] = useState(false)
  const [userOpen, setUserOpen] = useState(false)

  const allowed = filterWorkspacesByPermission(workspaces, can)
  const current = workspaceOfPath(allowed, pathname)

  const go = (path: string) => {
    setMenuOpen(false)
    navigate(path)
  }

  return (
    <>
      <MobileShellFrame
        contentMode="full"
        header={
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', paddingInline: 4 }}>
            <button
              type="button"
              aria-label="打开菜单"
              style={iconButton}
              onClick={() => setMenuOpen(true)}
            >
              <MenuIcon />
            </button>
            <div
              style={{
                flex: 1,
                minWidth: 0,
                textAlign: 'center',
                fontWeight: 600,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {current?.label ?? appConfig.name}
            </div>
            <div style={{ width: 40 }} />
          </div>
        }
      >
        <Outlet />
      </MobileShellFrame>

      <Popup
        visible={menuOpen}
        position="left"
        onMaskClick={() => setMenuOpen(false)}
        bodyStyle={{ width: '72vw', height: '100%', display: 'flex', flexDirection: 'column' }}
      >
        <Link
          to="/"
          onClick={() => setMenuOpen(false)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '16px 16px 8px',
            fontSize: 18,
            fontWeight: 600,
            color: colorTokens.brand,
            textDecoration: 'none',
          }}
        >
          <BrandLogo size={26} />
          {appConfig.name}
        </Link>

        <div style={{ flex: 1, overflow: 'auto' }}>
          <List>
            {allowed.map((workspace) => (
              <List.Item
                key={workspace.key}
                prefix={workspace.icon ?? <IconBox size={20} />}
                extra={current?.key === workspace.key ? '当前' : undefined}
                onClick={() => go(workspaceHomePath(workspace))}
              >
                {workspace.label}
              </List.Item>
            ))}
            {allowed.length === 0 && <List.Item>暂无可访问模块</List.Item>}
          </List>
        </div>

        <div
          style={{
            borderTop: `1px solid ${colorTokens.borderSecondary}`,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '8px 12px',
          }}
        >
          <UserAvatar name={me?.nickname ?? ''} src={me?.avatar} size={32} />
          <span
            style={{
              flex: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              fontWeight: 600,
            }}
          >
            {me?.nickname ?? ''}
          </span>
          <button
            type="button"
            aria-label="用户选项"
            style={iconButton}
            onClick={() => setUserOpen(true)}
          >
            <MoreIcon />
          </button>
        </div>
      </Popup>

      <ActionSheet
        visible={userOpen}
        actions={[{ key: 'logout', text: '退出登录', danger: true }]}
        cancelText="取消"
        onClose={() => setUserOpen(false)}
        onAction={(action) => {
          setUserOpen(false)
          if (action.key === 'logout') logout()
        }}
      />
    </>
  )
}
