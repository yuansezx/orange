import type { ReactNode } from 'react'

import { layoutTokens } from '@shared/theme/layout'
import { colorTokens } from '@shared/theme/tokens'

import styles from './shell.module.css'
import type { ContentMode } from './types'

interface Props {
  header: ReactNode
  contentMode?: ContentMode
  children: ReactNode
}

/** 移动壳：顶部栏 + 内容；左侧导航由页面用 Popup 承担。 */
export function MobileShellFrame({ header, contentMode = 'standard', children }: Props) {
  return (
    <div className={styles.mobileShell}>
      <header
        style={{
          height: layoutTokens.mobileHeaderHeight,
          flexShrink: 0,
          background: colorTokens.bgContainer,
          borderBottom: `1px solid ${colorTokens.borderSecondary}`,
        }}
      >
        {header}
      </header>
      <main
        className={styles.mobileContent}
        data-mode={contentMode}
        style={{ background: colorTokens.bgLayout }}
      >
        {children}
      </main>
    </div>
  )
}
