import type { ReactNode } from 'react'

/**
 * 应用壳内的一条菜单项——**同时承载它的路由**（菜单与路由一处声明，杜绝"菜单指向不存在的页"）。
 * 与后端约定：菜单归前端；`permission` 缺失即永远可见。
 */
export interface MenuLink {
  key: string
  label: string
  /** 相对应用壳的路径（如 `users` → `/admin/users`）。 */
  path: string
  /** 需要的功能权限码（`module:resource:action`）；缺省 = 永远可见。 */
  permission?: string
  /** 菜单图标（ReactNode）；缺省无图标。 */
  icon?: ReactNode
  element: ReactNode
}

/** 应用壳侧栏里的一个菜单分组（如 iam 组、系统监控组）。 */
export interface MenuGroup {
  key: string
  label: string
  /** 折叠轨道态下的分组图标。 */
  icon?: ReactNode
  links: MenuLink[]
}

export type SystemNavState = 'hidden' | 'rail' | 'expanded'
export type SystemNavBehavior = 'push' | 'overlay'

/** 系统栏的允许形态与默认值（由 workspace 声明，用户只能在允许集合内切换）。 */
export interface SystemNavPreference {
  defaultState?: SystemNavState
  behavior?: SystemNavBehavior
  allowedStates?: SystemNavState[]
}

/**
 * 用户视角的系统级模块（Workspace）。一个 workspace 可包含多个 feature：
 * 后台管理包含 iam / monitor；独立 feature 可自成一 workspace。
 * 路由：`{basePath}/{feature.name}/{path}`。
 */
export interface WorkspaceRef {
  key: string
  label: string
  basePath: string
  systemNav?: SystemNavPreference
}

/** 模块递给应用壳的布局偏好。 */
export interface ShellPreference {
  content?: 'standard' | 'full'
  /** v1 只实现 push；overlay 留给后续沉浸模块。 */
  leftMode?: 'push' | 'overlay'
}

/** 业务模块递给应用壳的菜单分组（由门面 `index.ts` 导出）。 */
export interface FeatureModule {
  name: string
  /** 模块级展示名（workspace 内部菜单用）；缺省回退到首个分组名或 name。 */
  label?: string
  icon?: ReactNode
  /** 归属的用户视角 workspace；缺省自成一 workspace。 */
  workspace?: WorkspaceRef
  shell?: ShellPreference
  groups?: MenuGroup[]
}

/** 聚合后的菜单项：在 MenuLink 基础上补完整路径与归属。 */
export interface NavLink extends MenuLink {
  /** 不含前导 `/` 的完整路径，如 `admin/iam/users`。 */
  fullPath: string
  /** 相对 workspace 的路径，如 `iam/users`。 */
  featurePath: string
  featureKey: string
  workspaceKey: string
  shell?: ShellPreference
}

/** 聚合后的菜单分组。 */
export interface NavGroup extends Omit<MenuGroup, 'links'> {
  links: NavLink[]
}
