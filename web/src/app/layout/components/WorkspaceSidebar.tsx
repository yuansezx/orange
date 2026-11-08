import { Menu } from 'antd'
import type { MenuProps } from 'antd'

import type { NavLink } from '@shared/navigation'
import { layoutTokens } from '@shared/theme/layout'
import { useWorkspacePalette } from '@shared/theme/workspacePaletteContext'

import type { WorkspaceNav } from '../../routes'

interface Props {
  workspace: WorkspaceNav
  selectedKey?: string
  onNavigate: (link: NavLink) => void
}

/** workspace 级侧栏（secondary navigation）：标题 + 菜单，占默认布局的第一列。 */
export function WorkspaceSidebar({ workspace, selectedKey, onNavigate }: Props) {
  const palette = useWorkspacePalette()
  /** 隐藏链接只注册路由，不进 navigation。 */
  const visibleLinks = workspace.features.flatMap((feature) =>
    feature.groups.flatMap((group) => group.links.filter((link) => !link.hidden)),
  )

  const sections = workspace.features.flatMap((feature) =>
    feature.groups
      .map((group) => ({
        key: `${feature.key}:${group.key}`,
        label:
          feature.groups.length === 1
            ? feature.label
            : `${feature.label} · ${group.label}`,
        links: group.links.filter((link) => !link.hidden),
      }))
      .filter((section) => section.links.length > 0),
  )

  // 始终按模块（feature）分组：workspace 只有一个模块时也保留分组头，
  // 避免后续加入新模块时导航层次突然从"平铺"变成"分组"。
  const items: MenuProps['items'] = sections.map((section) => ({
    key: section.key,
    type: 'group' as const,
    label: section.label,
    children: section.links.map((link) => ({
      key: link.key,
      icon: link.icon,
      label: link.label,
    })),
  }))

  return (
    <aside
      style={{
        minWidth: 0,
        overflow: 'hidden',
        borderRight: `1px solid ${palette.navBorder}`,
        background: palette.navBg,
      }}
    >
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div
          style={{
            height: layoutTokens.headerHeight,
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
            paddingInline: 16,
            borderBottom: `1px solid ${palette.borderSecondary}`,
            fontWeight: 600,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {workspace.label}
        </div>

        <div style={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
          {/* Menu 默认用 colorBgContainer 刷根背景，必须显式覆盖成 workspace 左栏底色 */}
          <Menu
            mode="inline"
            style={{ borderInlineEnd: 0, background: palette.navBg }}
            selectedKeys={selectedKey ? [selectedKey] : []}
            items={items}
            onClick={({ key }) => {
              const link = visibleLinks.find((item) => item.key === key)
              if (link) onNavigate(link)
            }}
          />
        </div>
      </div>
    </aside>
  )
}
