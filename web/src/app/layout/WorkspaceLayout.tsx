import { Empty, Select } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { usePermission } from '@features/auth'
import { matchNavLink } from '@shared/navigation'
import { Platform } from '@shared/platform'
import { ShellRightPanel, ShellRightPanelProvider } from '@shared/shell'
import { layoutTokens } from '@shared/theme/layout'
import { colorTokens } from '@shared/theme/tokens'

import {
  filterWorkspacesByPermission,
  type WorkspaceNav,
} from '../routes'
import { WorkspaceMenu } from './components/WorkspaceMenu'

interface Props {
  workspace: WorkspaceNav
}

/**
 * 标准 workspace 壳（在系统内容区里）：
 * 桌面 = 左菜单 + 内容 + 右详情栏；移动 = 顶部页面选择 + 内容（暂定，后续单独适配）。
 */
export function WorkspaceLayout({ workspace }: Props) {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { can } = usePermission()

  const filtered = filterWorkspacesByPermission([workspace], can)[0]
  const links =
    filtered?.features.flatMap((feature) =>
      feature.groups.flatMap((group) => group.links),
    ) ?? []
  const current = matchNavLink(links, pathname)

  if (!filtered || links.length === 0) {
    return <Empty description="暂无可访问页面" style={{ marginTop: 80 }} />
  }

  const contentPadding = current?.shell?.content === 'full' ? 0 : layoutTokens.contentPadding

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
        <WorkspaceMenu
          workspace={filtered}
          selectedKey={current?.key}
          onNavigate={(link) => navigate(`/${link.fullPath}`)}
        />
      </aside>
      <main
        style={{
          minWidth: 0,
          overflow: 'auto',
          padding: contentPadding,
        }}
      >
        <Outlet />
      </main>
    </div>
  )

  // 移动端暂用页面选择器，避免抽屉套抽屉；后续再单独规划。
  const options = filtered.features.map((feature) => ({
    label: feature.label,
    options: feature.groups
      .flatMap((group) => group.links)
      .map((link) => ({ label: link.label, value: link.key })),
  }))

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
          placeholder="选择页面"
          value={current?.key}
          options={options}
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
          padding: current?.shell?.content === 'full' ? 0 : layoutTokens.mobileContentPadding,
        }}
      >
        <Outlet />
      </main>
    </div>
  )

  return (
    <ShellRightPanelProvider>
      <Platform desktop={desktop} mobile={mobile} />
      <ShellRightPanel />
    </ShellRightPanelProvider>
  )
}
