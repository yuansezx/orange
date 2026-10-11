import { Layout, Menu } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { appConfig } from '@shared/config'
import { colorTokens } from '@shared/theme/tokens'

import { navItems } from '../../routes'

const { Sider, Header, Content } = Layout

export function DesktopLayout() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const activeKey = navItems.find((item) => pathname.startsWith(item.path))?.key

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={220}>
        <div
          style={{
            height: 56,
            display: 'flex',
            alignItems: 'center',
            paddingInline: 20,
            fontSize: 18,
            fontWeight: 600,
            color: colorTokens.brand,
          }}
        >
          {appConfig.name}
        </div>
        <Menu
          mode="inline"
          selectedKeys={activeKey ? [activeKey] : []}
          items={navItems.map((item) => ({ key: item.key, label: item.label }))}
          onClick={({ key }) => {
            const item = navItems.find((nav) => nav.key === key)
            if (item) navigate(item.path)
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
          <span style={{ color: colorTokens.textTertiary, fontSize: 12 }}>
            v{appConfig.version}
          </span>
        </Header>
        <Content style={{ padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
