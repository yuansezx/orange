import { Dropdown, Layout, Menu } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { useLogout, usePermission } from '@features/auth'
import { appConfig } from '@shared/config'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo, UserAvatar } from '@shared/ui'

import { ADMIN_PATH } from '../../navigation'
import { menuGroups } from '../../routes'

const { Sider, Header, Content } = Layout

/** 后台管理壳 · 桌面：左栏分组菜单（按权限过滤）+ 顶栏（右：版本 + 用户菜单）+ 内容区。 */
export function DesktopAdminShell() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { can, me } = usePermission()
  const { logout } = useLogout()

  // 过滤：只留有权限的链接；组内空了整组不显示
  const groups = menuGroups
    .map((group) => ({ ...group, links: group.links.filter((link) => can(link.permission)) }))
    .filter((group) => group.links.length > 0)
  const links = groups.flatMap((group) => group.links)
  const selectedKey = links.find((link) => pathname.endsWith(`/${link.path}`))?.key

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={220}>
        <div
          style={{
            height: 56,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            paddingInline: 20,
            fontSize: 18,
            fontWeight: 600,
            color: colorTokens.brand,
          }}
        >
          <BrandLogo size={26} />
          {appConfig.name}
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedKey ? [selectedKey] : []}
          defaultOpenKeys={groups.map((group) => group.key)}
          items={groups.map((group) => ({
            key: group.key,
            label: group.label,
            children: group.links.map((link) => ({ key: link.key, label: link.label })),
          }))}
          onClick={({ key }) => {
            const link = links.find((item) => item.key === key)
            if (link) navigate(`${ADMIN_PATH}/${link.path}`)
          }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: colorTokens.bgContainer,
            paddingInline: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            gap: 16,
          }}
        >
          <span style={{ color: colorTokens.textTertiary, fontSize: 12 }}>
            v{appConfig.version}
          </span>
          {me && (
            <Dropdown
              trigger={['click']}
              placement="bottomRight"
              menu={{
                items: [{ key: 'logout', label: '退出登录', danger: true }],
                onClick: ({ key }) => {
                  if (key === 'logout') logout()
                },
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  maxWidth: 180,
                  cursor: 'pointer',
                }}
              >
                <UserAvatar name={me.nickname} src={me.avatar} size={28} />
                <span
                  style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                >
                  {me.nickname}
                </span>
              </div>
            </Dropdown>
          )}
        </Header>
        <Content style={{ padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
