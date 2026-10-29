import type { ComponentType, ReactNode } from 'react'

import type { WorkspacePalette } from '@shared/theme/tokens'

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

export type SystemSidebarState = 'hidden' | 'rail' | 'expanded'
export type SystemSidebarBehavior = 'push' | 'overlay'

/** 自定义 workspace 布局能拿到的最小 workspace 信息（shared 层不认识完整 WorkspaceNav）。 */
export interface WorkspaceDescriptor {
  key: string
  label: string
  basePath: string
}

/**
 * workspace 自定义布局逃生口：组件自行渲染 `<Outlet />`，可不要默认左/右栏。
 * 系统壳与 `WorkspaceThemeProvider` 仍在外层；详情右栏的 context 也会提供，
 * 需要时自己渲染 `<WorkspaceContextPanel />`。
 */
export type WorkspaceLayoutComponent = ComponentType<{ workspace: WorkspaceDescriptor }>

/**
 * 用户视角的系统级模块（Workspace）。一个 workspace 可包含多个 feature：
 * 后台管理包含 iam / monitor；独立 feature 可自成一 workspace。
 * 路由：`{basePath}/{feature.name}/{path}`。
 */
export interface WorkspaceRef {
  key: string
  label: string
  basePath: string
  /**
   * workspace 内容与系统栏的关系：`push` 挤占 / `overlay` 悬浮。
   * 系统栏的三态与默认值归系统统一管理，workspace 不参与。
   */
  systemSidebarBehavior?: SystemSidebarBehavior
  /** workspace 级配色覆盖；缺省用 `defaultWorkspacePalette`。 */
  theme?: Partial<WorkspacePalette>
  /** 自定义 workspace 布局；缺省用统一 `WorkspaceLayout`（左中右）。 */
  layout?: WorkspaceLayoutComponent
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
  /** 该模块向「个人中心」贡献的设置分组。 */
  settings?: SettingsGroup[]
}

/** 模块贡献给个人中心的设置分组（path 相对 `/account/{feature}`）。 */
export interface SettingsGroup {
  key: string
  label: string
  links: MenuLink[]
}

/** 聚合后的个人中心设置链接。 */
export interface AccountSettingsLink extends MenuLink {
  /** 相对 `/account` 的路径，如 `iam/profile`。 */
  settingsPath: string
  /** 不含前导 `/` 的完整路径，如 `account/iam/profile`。 */
  fullPath: string
  featureKey: string
}

export interface AccountSettingsGroup extends Omit<SettingsGroup, 'links'> {
  links: AccountSettingsLink[]
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
