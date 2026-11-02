import type { ReactNode } from 'react'

import type { SystemSidebarBehavior, SystemSidebarState } from '@shared/navigation'
import { layoutTokens } from '@shared/theme/layout'
import { colorTokens } from '@shared/theme/tokens'

interface Props {
  /** 系统侧栏内容（rail / expanded）。 */
  sidebar: ReactNode
  sidebarState: SystemSidebarState
  sidebarBehavior: SystemSidebarBehavior
  /** hidden 状态下的悬浮唤出按钮。 */
  trigger: ReactNode
  children: ReactNode
}

/**
 * 桌面系统壳：单一常驻 DOM，侧栏三态 × push/overlay 只切样式。
 * 侧栏与主内容在树中的位置固定——切换 workspace 或展开行为时不会 remount。
 */
export function DesktopShellFrame({
  sidebar,
  sidebarState,
  sidebarBehavior,
  trigger,
  children,
}: Props) {
  const visible = sidebarState !== 'hidden'
  const sidebarWidth =
    sidebarState === 'expanded'
      ? layoutTokens.systemSidebarExpandedWidth
      : layoutTokens.systemSidebarRailWidth
  const overlay = sidebarBehavior === 'overlay'

  // overlay：侧栏脱离布局流（fixed），轨道保持 0，主内容占满；
  // push：侧栏占第一列，轨道宽度随展开状态过渡。
  const trackWidth = overlay ? 0 : visible ? sidebarWidth : 0

  const sidebarStyle = {
    width: sidebarWidth,
    background: colorTokens.bgSystemSidebar,
    borderRight: `1px solid ${colorTokens.border}`,
    overflow: 'hidden',
    ...(overlay
      ? {
          position: 'fixed' as const,
          left: 0,
          top: 0,
          height: '100vh',
          zIndex: 90,
          boxShadow: '8px 0 24px rgba(0, 0, 0, 0.08)',
        }
      : null),
  }

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `${trackWidth}px minmax(0, 1fr)`,
        height: '100vh',
        overflow: 'hidden',
        background: colorTokens.bgLayout,
        transition: 'grid-template-columns 200ms ease',
      }}
    >
      {visible && <aside style={sidebarStyle}>{sidebar}</aside>}
      {/* hidden 时第一列宽度为 0，主内容仍显式放第二列 */}
      <main style={{ gridColumn: 2, minWidth: 0, height: '100vh', overflow: 'hidden' }}>
        {children}
      </main>
      {!visible && (
        <div style={{ position: 'fixed', left: 12, bottom: 12, zIndex: 95 }}>
          {trigger}
        </div>
      )}
    </div>
  )
}
