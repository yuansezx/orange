import { Menu } from 'antd'
import type { MenuProps } from 'antd'

import type { NavLink } from '@shared/navigation'
import { layoutTokens } from '@shared/theme/layout'
import { colorTokens } from '@shared/theme/tokens'

import type { WorkspaceNav } from '../../routes'

interface Props {
  workspace: WorkspaceNav
  selectedKey?: string
  onNavigate: (link: NavLink) => void
}

/** workspace 自己的内部菜单（内容区左侧）。 */
export function WorkspaceMenu({ workspace, selectedKey, onNavigate }: Props) {
  const links = workspace.features.flatMap((feature) =>
    feature.groups.flatMap((group) => group.links),
  )

  const sections = workspace.features.flatMap((feature) =>
    feature.groups.map((group) => ({
      key: `${feature.key}:${group.key}`,
      label:
        feature.groups.length === 1
          ? feature.label
          : `${feature.label} · ${group.label}`,
      links: group.links,
    })),
  )

  const items: MenuProps['items'] =
    sections.length === 1
      ? sections[0].links.map((link) => ({
          key: link.key,
          icon: link.icon,
          label: link.label,
        }))
      : sections.map((section) => ({
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
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div
        style={{
          height: layoutTokens.headerHeight,
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          paddingInline: 16,
          borderBottom: `1px solid ${colorTokens.borderSecondary}`,
          fontWeight: 600,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {workspace.label}
      </div>

      <div style={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
        <Menu
          mode="inline"
          style={{ borderInlineEnd: 0 }}
          selectedKeys={selectedKey ? [selectedKey] : []}
          items={items}
          onClick={({ key }) => {
            const link = links.find((item) => item.key === key)
            if (link) onNavigate(link)
          }}
        />
      </div>
    </div>
  )
}
