import { Button, Card } from 'antd'
import { Link } from 'react-router-dom'

import { useLogout } from '@features/auth'
import { appConfig } from '@shared/config'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo } from '@shared/ui'

import { navEntries } from '../navigation'

/** 导航页 —— 登录后的入口列表，每个入口进入一个应用壳。 */
export function NavHome() {
  const { logout } = useLogout()

  return (
    <div style={{ minHeight: '100vh', background: colorTokens.borderSecondary }}>
      <header
        style={{
          height: 56,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          paddingInline: 24,
          background: colorTokens.bgContainer,
          borderBottom: `1px solid ${colorTokens.borderSecondary}`,
        }}
      >
        <BrandLogo size={26} />
        <span style={{ fontSize: 18, fontWeight: 600, color: colorTokens.brand }}>
          {appConfig.name}
        </span>
        <Button type="link" style={{ marginLeft: 'auto' }} onClick={() => logout()}>
          退出登录
        </Button>
      </header>

      <main style={{ maxWidth: 960, margin: '0 auto', padding: 24 }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: 16,
          }}
        >
          {navEntries.map((entry) => (
            <Link key={entry.key} to={entry.path}>
              <Card hoverable>{entry.label}</Card>
            </Link>
          ))}
        </div>
      </main>
    </div>
  )
}
