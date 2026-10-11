import { ActionSheet, List, Popup } from 'antd-mobile'
import { useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { useLogout, usePermission } from '@features/auth'
import { appConfig } from '@shared/config'
import { matchMenuLink } from '@shared/navigation'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo, UserAvatar } from '@shared/ui'

import { ADMIN_PATH } from '../../navigation'
import { menuGroups } from '../../routes'

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

/** 后台管理壳 · 移动：顶栏（汉堡在左、中间当前菜单名，sticky）+ 内容区 + 左侧抽屉（底部用户区）。 */
export function MobileAdminShell() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { can, me } = usePermission()
  const { logout } = useLogout()
  const [menuOpen, setMenuOpen] = useState(false)
  const [userOpen, setUserOpen] = useState(false)

  const groups = menuGroups
    .map((group) => ({ ...group, links: group.links.filter((link) => can(link.permission)) }))
    .filter((group) => group.links.length > 0)
  const links = groups.flatMap((group) => group.links)
  const current = matchMenuLink(links, pathname, ADMIN_PATH)

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 10,
          height: 48,
          display: 'flex',
          alignItems: 'center',
          paddingInline: 4,
          background: colorTokens.bgContainer,
          borderBottom: `1px solid ${colorTokens.borderSecondary}`,
        }}
      >
        <button type="button" aria-label="打开菜单" style={iconButton} onClick={() => setMenuOpen(true)}>
          <MenuIcon />
        </button>
        <div style={{ flex: 1, textAlign: 'center', fontWeight: 600 }}>
          {current?.label ?? appConfig.name}
        </div>
        <div style={{ width: 40 }} />
      </header>

      <main style={{ flex: 1, overflow: 'auto', padding: 12 }}>
        <Outlet />
      </main>

      <Popup
        visible={menuOpen}
        position="left"
        onMaskClick={() => setMenuOpen(false)}
        bodyStyle={{ width: '72vw', height: '100%', display: 'flex', flexDirection: 'column' }}
      >
        {/* 顶部：logo + 应用名 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '16px 16px 8px',
            fontSize: 18,
            fontWeight: 600,
            color: colorTokens.brand,
          }}
        >
          <BrandLogo size={26} />
          {appConfig.name}
        </div>

        {/* 中部：分组菜单（可滚动） */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {groups.map((group) => (
            <div key={group.key}>
              <div style={{ padding: '10px 16px 4px', fontSize: 12, color: colorTokens.textTertiary }}>
                {group.label}
              </div>
              <List>
                {group.links.map((link) => (
                  <List.Item
                    key={link.key}
                    onClick={() => {
                      setMenuOpen(false)
                      navigate(`${ADMIN_PATH}/${link.path}`)
                    }}
                  >
                    {link.label}
                  </List.Item>
                ))}
              </List>
            </div>
          ))}
        </div>

        {/* 底部：头像 + 昵称 + 更多（三点） */}
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
          <button type="button" aria-label="用户选项" style={iconButton} onClick={() => setUserOpen(true)}>
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
    </div>
  )
}
