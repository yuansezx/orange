import type { ReactNode } from 'react'

import type {
  FeatureModule,
  MenuLink,
  NavGroup,
  NavLink,
  SystemNavPreference,
  WorkspaceRef,
} from '@shared/navigation'

/**
 * 组合根：**构建期发现**模块型切片——扫描 `features/<module>/index.ts`，取门面导出的 `feature`。
 *
 * 用 glob 而非硬编码清单：目录不存在即跳过。这样开源仓缺少闭源模块时不会出现
 * 指向不存在目录的 import，新增模块也不必回来登记。控制台级切片（如 auth）
 * 不导出 `feature`，自然不进入本表。
 *
 * 运行时不做模块开关：可见性由后端权限码过滤菜单承担，前端不再放第二份「启用清单」。
 */
const discovered = import.meta.glob<{ feature?: FeatureModule }>('../features/*/index.ts', {
  eager: true,
})

export const features: FeatureModule[] = Object.keys(discovered)
  .sort()
  .map((path) => discovered[path].feature)
  .filter((feature): feature is FeatureModule => feature !== undefined)

/** workspace 内部的 feature（实现模块）。 */
export interface FeatureNav {
  key: string
  label: string
  icon?: ReactNode
  groups: NavGroup[]
}

/**
 * 用户视角的系统级模块。一个 workspace 可包含多个 feature：
 * 后台管理（admin）= iam + monitor；无 workspace 声明的 feature 自成一 workspace。
 */
export interface WorkspaceNav {
  key: string
  label: string
  icon?: ReactNode
  basePath: string
  systemNav?: SystemNavPreference
  features: FeatureNav[]
}

function workspaceOfFeature(feature: FeatureModule, fallbackLabel: string): WorkspaceRef {
  return (
    feature.workspace ?? {
      key: feature.name,
      label: feature.label ?? fallbackLabel,
      basePath: feature.name,
    }
  )
}

function toNavLink(
  workspace: WorkspaceRef,
  feature: FeatureModule,
  link: MenuLink,
): NavLink {
  return {
    ...link,
    fullPath: `${workspace.basePath}/${feature.name}/${link.path}`,
    featurePath: `${feature.name}/${link.path}`,
    featureKey: feature.name,
    workspaceKey: workspace.key,
    shell: feature.shell,
  }
}

const workspaceMap = new Map<string, WorkspaceNav>()

for (const feature of features) {
  const groups = (feature.groups ?? []).map((group) => {
    const workspace = workspaceOfFeature(feature, group.label)
    return {
      ...group,
      links: group.links.map((link) => toNavLink(workspace, feature, link)),
    }
  })
  if (groups.length === 0) continue

  const workspaceRef = workspaceOfFeature(feature, groups[0].label)
  let workspace = workspaceMap.get(workspaceRef.key)
  if (!workspace) {
    workspace = {
      key: workspaceRef.key,
      label: workspaceRef.label,
      icon: feature.icon,
      basePath: workspaceRef.basePath,
      systemNav: workspaceRef.systemNav,
      features: [],
    }
    workspaceMap.set(workspaceRef.key, workspace)
  }
  if (!workspace.icon) workspace.icon = feature.icon

  workspace.features.push({
    key: feature.name,
    label: feature.label ?? groups[0].label,
    icon: feature.icon,
    groups,
  })
}

/** 系统级 workspace 列表（含内部的 feature/菜单）。 */
export const workspaces: WorkspaceNav[] = [...workspaceMap.values()]

/** 拉平后的全部菜单项（路由注册/当前页匹配用）。 */
export const menuLinks: NavLink[] = workspaces.flatMap((workspace) =>
  workspace.features.flatMap((feature) =>
    feature.groups.flatMap((group) => group.links),
  ),
)

/** 按功能权限过滤；feature 无可见页面则隐藏，workspace 全空则隐藏。 */
export function filterWorkspacesByPermission(
  items: WorkspaceNav[],
  can: (permission?: string) => boolean,
): WorkspaceNav[] {
  return items
    .map((workspace) => ({
      ...workspace,
      features: workspace.features
        .map((feature) => ({
          ...feature,
          groups: feature.groups
            .map((group) => ({
              ...group,
              links: group.links.filter((link) => can(link.permission)),
            }))
            .filter((group) => group.links.length > 0),
        }))
        .filter((feature) => feature.groups.length > 0),
    }))
    .filter((workspace) => workspace.features.length > 0)
}

/** workspace 默认落地页：第一个有权限的 feature 页面。 */
export function workspaceHomePath(workspace: WorkspaceNav): string {
  const link = workspace.features[0]?.groups[0]?.links[0]
  return link ? `/${link.fullPath}` : '/'
}

/** 当前 pathname 所属 workspace。 */
export function workspaceOfPath(
  items: WorkspaceNav[],
  pathname: string,
): WorkspaceNav | undefined {
  return items.find(
    (workspace) =>
      pathname === `/${workspace.basePath}` ||
      pathname.startsWith(`/${workspace.basePath}/`),
  )
}
