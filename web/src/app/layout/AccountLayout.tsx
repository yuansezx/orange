import { Empty, Menu, Select } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { usePermission } from '@features/auth'
import { matchNavLink } from '@shared/navigation'
import { Platform } from '@shared/platform'
import { layoutTokens } from '@shared/theme/layout'
import { colorTokens } from '@shared/theme/tokens'

import {
  accountSettings,
  filterAccountSettings,
} from '../routes'

/** 个人中心：系统级页面，左菜单由各 feature 的 `settings` 聚合而来。 */
export function AccountLayout() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { can } = usePermission()

  const groups = filterAccountSettings(accountSettings, can)
  const links = groups.flatMap((group) => group.links)
  const current = matchNavLink(links, pathname)

  if (links.length === 0) {
    return <Empty description="暂无可用设置" style={{ marginTop: 80 }} />
  }

  const desktop = (
    <div
      style={{
        height: '100%',
        display: 'grid',
        gridTemplateColumns: `${layoutTokens.workspaceMenuWidth}px minmax(0, 1fr)`,
        overflow: 'hidden',
      }}
    >
      <aside
        style={{
          minWidth: 0,
          overflow: 'hidden',
          borderRight: `1px solid ${colorTokens.borderSecondary}`,
          background: colorTokens.bgContainer,
        }}
      >
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <div
            style={{
              height: layoutTokens.headerHeight,
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              paddingInline: 16,
              borderBottom: `1px solid ${colorTokens.borderSecondary}`,
              fontWeight: 600,
            }}
          >
            个人中心
          </div>
          <div style={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
            <Menu
              mode="inline"
              style={{ borderInlineEnd: 0 }}
              selectedKeys={current ? [current.key] : []}
              items={groups.map((group) => ({
                key: group.key,
                type: 'group',
                label: group.label,
                children: group.links.map((link) => ({
                  key: link.key,
                  icon: link.icon,
                  label: link.label,
                })),
              }))}
              onClick={({ key }) => {
                const link = links.find((item) => item.key === key)
                if (link) navigate(`/${link.fullPath}`)
              }}
            />
          </div>
        </div>
      </aside>

      <main style={{ minWidth: 0, overflow: 'auto', padding: layoutTokens.contentPadding }}>
        <Outlet />
      </main>
    </div>
  )

  const mobile = (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div
        style={{
          flexShrink: 0,
          padding: 8,
          borderBottom: `1px solid ${colorTokens.borderSecondary}`,
        }}
      >
        <Select
          style={{ width: '100%' }}
          placeholder="选择设置"
          value={current?.key}
          options={groups.map((group) => ({
            label: group.label,
            options: group.links.map((link) => ({
              label: link.label,
              value: link.key,
            })),
          }))}
          onChange={(key) => {
            const link = links.find((item) => item.key === key)
            if (link) navigate(`/${link.fullPath}`)
          }}
        />
      </div>
      <main
        style={{
          flex: 1,
          minHeight: 0,
          overflow: 'auto',
          padding: layoutTokens.mobileContentPadding,
        }}
      >
        <Outlet />
      </main>
    </div>
  )

  return <Platform desktop={desktop} mobile={mobile} />
}
