import { Layout, Menu } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { UserMenu, usePermission } from '@features/auth'
import { appConfig } from '@shared/config'
import { matchMenuLink } from '@shared/navigation'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo } from '@shared/ui'

import { ADMIN_PATH } from '../../navigation'
import { menuGroups } from '../../routes'

const { Sider, Header, Content } = Layout

/** 后台管理壳 · 桌面：左栏分组菜单（按权限过滤）+ 顶栏（右：用户区）+ 内容区。 */
export function DesktopAdminShell() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { can } = usePermission()

  // 过滤：只留有权限的链接；组内空了整组不显示
  const groups = menuGroups
    .map((group) => ({ ...group, links: group.links.filter((link) => can(link.permission)) }))
    .filter((group) => group.links.length > 0)
  const links = groups.flatMap((group) => group.links)

  // 当前路由 → 选中项 + 其所属分组（直接粘 URL / 回跳进来也对）
  const selectedKey = matchMenuLink(links, pathname, ADMIN_PATH)?.key
  const activeGroupKey = groups.find((group) =>
    group.links.some((link) => link.key === selectedKey),
  )?.key

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
          // key 绑当前分组：路由换了分组就重挂，默认展开随之切到该分组
          key={activeGroupKey ?? 'none'}
          mode="inline"
          selectedKeys={selectedKey ? [selectedKey] : []}
          defaultOpenKeys={activeGroupKey ? [activeGroupKey] : []}
          items={groups.map((group) => ({
            key: group.key,
            label: group.label,
            children: group.links.map((link) => ({
              key: link.key,
              icon: link.icon,
              label: link.label,
            })),
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
          }}
        >
          <UserMenu />
        </Header>
        <Content style={{ padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
