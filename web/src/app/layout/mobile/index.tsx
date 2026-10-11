import { TabBar } from 'antd-mobile'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { appConfig } from '@shared/config'

import { navItems } from '../../routes'

export function MobileLayout() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const activeKey = navItems.find((item) => pathname.startsWith(item.path))?.key

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          height: 48,
          display: 'flex',
          alignItems: 'center',
          paddingInline: 16,
          fontWeight: 600,
          color: '#f5822b',
          borderBottom: '1px solid #f0f0f0',
          background: '#fff',
        }}
      >
        {appConfig.name}
      </header>
      <main style={{ flex: 1, overflow: 'auto', padding: 12 }}>
        <Outlet />
      </main>
      <nav style={{ borderTop: '1px solid #f0f0f0', background: '#fff' }}>
        <TabBar
          activeKey={activeKey}
          onChange={(key) => {
            const item = navItems.find((nav) => nav.key === key)
            if (item) navigate(item.path)
          }}
        >
          {navItems.map((item) => (
            <TabBar.Item key={item.key} title={item.label} />
          ))}
        </TabBar>
      </nav>
    </div>
  )
}
