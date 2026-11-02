import { Empty, Select } from 'antd'
import { useMemo } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { usePermission } from '@features/auth'
import { matchNavLink } from '@shared/navigation'
import { Platform } from '@shared/platform'
import { WorkspaceContextPanel, WorkspaceContextPanelProvider } from '@shared/shell'
import { layoutTokens } from '@shared/theme/layout'
import { resolveWorkspacePalette } from '@shared/theme/tokens'
import { WorkspaceThemeProvider } from '@shared/theme/WorkspaceTheme'

import {
  filterWorkspacesByPermission,
  type WorkspaceNav,
} from '../routes'
import { WorkspaceSidebar } from './components/WorkspaceSidebar'

interface Props {
  workspace: WorkspaceNav
}

/**
 * 默认 workspace 壳（在系统内容区里展开）：
 * 桌面 = WorkspaceSidebar + workspace 内容区 + WorkspaceContextPanel；
 * 移动 = 顶部页面选择 + 内容（暂定，后续单独适配）。
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
  /** workspace 调色板：未声明的项回退默认（系统壳不受影响）。 */
  const palette = useMemo(
    () => resolveWorkspacePalette(filtered?.theme),
    [filtered?.theme],
  )

  if (!filtered || links.length === 0) {
    return <Empty description="暂无可访问页面" style={{ marginTop: 80 }} />
  }

  const contentPadding = current?.shell?.content === 'full' ? 0 : layoutTokens.contentPadding

  // 逃生口：workspace 自带布局时完全接管内部结构（自行渲染 <Outlet />）。
  // 主题 provider 与外层系统壳仍然有效。
  const CustomLayout = filtered.layout
  if (CustomLayout) {
    return (
      <WorkspaceThemeProvider palette={palette}>
        <WorkspaceContextPanelProvider>
          <CustomLayout workspace={filtered} />
        </WorkspaceContextPanelProvider>
      </WorkspaceThemeProvider>
    )
  }

  const desktop = (
    <div
      style={{
        height: '100%',
        display: 'grid',
        gridTemplateColumns: `${layoutTokens.workspaceSidebarWidth}px minmax(0, 1fr)`,
        overflow: 'hidden',
      }}
    >
      <WorkspaceSidebar
        workspace={filtered}
        selectedKey={current?.key}
        onNavigate={(link) => navigate(`/${link.fullPath}`)}
      />
      <main
        style={{
          minWidth: 0,
          overflow: 'auto',
          padding: contentPadding,
          background: palette.canvasBg,
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
          borderBottom: `1px solid ${palette.borderSecondary}`,
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
          background: palette.canvasBg,
        }}
      >
        <Outlet />
      </main>
    </div>
  )

  return (
    <WorkspaceThemeProvider palette={palette}>
      <WorkspaceContextPanelProvider>
        <Platform desktop={desktop} mobile={mobile} />
        <WorkspaceContextPanel />
      </WorkspaceContextPanelProvider>
    </WorkspaceThemeProvider>
  )
}
