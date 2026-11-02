import { Card, Typography, theme } from 'antd'
import type { CSSProperties } from 'react'

import { appConfig } from '@shared/config'
import { colorTokens } from '@shared/theme/tokens'
import { BrandLogo } from '@shared/ui'

import { LoginForm } from './components/LoginForm'
import { useLogin } from './hooks/useLogin'

/** 品牌光斑：模糊的大色团，做背景环境光（纯装饰）。 */
function BrandGlow(props: { style: CSSProperties }) {
  return (
    <div
      aria-hidden
      style={{
        position: 'absolute',
        borderRadius: '50%',
        background: colorTokens.brand,
        filter: 'blur(90px)',
        pointerEvents: 'none',
        ...props.style,
      }}
    />
  )
}

/** 登录页（控制台级切口，**在应用壳之外**）。 */
export function LoginPage() {
  const { submit, loading } = useLogin()
  const { token } = theme.useToken()
  const { brandSoft, bgContainer } = colorTokens

  return (
    <div
      style={{
        position: 'relative',
        overflow: 'hidden',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
        // 品牌浅色底 → 容器白 的柔和渐变；换品牌色自动跟随
        background: `linear-gradient(160deg, ${brandSoft} 0%, ${bgContainer} 62%)`,
      }}
    >
      {/* 两团品牌光晕（左上 / 右下），营造环境光 */}
      <BrandGlow style={{ width: 440, height: 440, top: -140, left: -120, opacity: 0.16 }} />
      <BrandGlow style={{ width: 380, height: 380, bottom: -150, right: -100, opacity: 0.1 }} />

      <Card
        style={{
          position: 'relative',
          width: 380,
          maxWidth: '100%',
          boxShadow: token.boxShadowSecondary,
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          {/* 品牌 logo（public/logo.svg 提供） */}
          <BrandLogo size={48} />
          <Typography.Title level={3} style={{ marginTop: 16, marginBottom: 4 }}>
            {appConfig.name}
          </Typography.Title>
          <Typography.Text type="secondary">欢迎回来，请登录</Typography.Text>
        </div>
        <LoginForm loading={loading} onSubmit={submit} />
      </Card>
    </div>
  )
}
