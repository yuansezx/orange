import type { ReactNode } from 'react'

import type { SystemNavBehavior, SystemNavState } from '@shared/navigation'
import { layoutTokens } from '@shared/theme/layout'
import { colorTokens } from '@shared/theme/tokens'

interface Props {
  /** 系统栏内容（rail/expanded）。 */
  nav: ReactNode
  navState: SystemNavState
  navBehavior: SystemNavBehavior
  /** hidden 状态下的悬浮唤出按钮。 */
  trigger: ReactNode
  children: ReactNode
}

/** 桌面系统壳：系统栏三态 × push/overlay，内容区交给 workspace。 */
export function DesktopShellFrame({
  nav,
  navState,
  navBehavior,
  trigger,
  children,
}: Props) {
  const visible = navState !== 'hidden'
  const navWidth =
    navState === 'expanded'
      ? layoutTokens.systemNavExpandedWidth
      : layoutTokens.railWidth

  const navStyle = {
    width: navWidth,
    background: colorTokens.bgContainer,
    borderRight: `1px solid ${colorTokens.borderSecondary}`,
    overflow: 'hidden',
  } as const

  const floatingTrigger = !visible && (
    <div style={{ position: 'fixed', left: 12, bottom: 12, zIndex: 95 }}>{trigger}</div>
  )

  if (navBehavior === 'overlay') {
    return (
      <div style={{ position: 'relative', height: '100vh', overflow: 'hidden' }}>
        <main style={{ height: '100vh', minWidth: 0, overflow: 'hidden' }}>{children}</main>
        {visible && (
          <aside
            style={{
              ...navStyle,
              position: 'fixed',
              left: 0,
              top: 0,
              height: '100vh',
              zIndex: 90,
              boxShadow: '8px 0 24px rgba(0, 0, 0, 0.08)',
            }}
          >
            {nav}
          </aside>
        )}
        {floatingTrigger}
      </div>
    )
  }

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `${visible ? navWidth : 0}px minmax(0, 1fr)`,
        height: '100vh',
        overflow: 'hidden',
        transition: 'grid-template-columns 200ms ease',
      }}
    >
      {visible && <aside style={navStyle}>{nav}</aside>}
      {/* 必须显式放第二列：hidden 时唯一的普通子元素不能被自动放进 0px 的第一列 */}
      <main
        style={{ gridColumn: 2, minWidth: 0, height: '100vh', overflow: 'hidden' }}
      >
        {children}
      </main>
      {floatingTrigger}
    </div>
  )
}
