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
  element: ReactNode
}

/** 应用壳侧栏里的一个菜单分组（如 iam 组、系统监控组）。 */
export interface MenuGroup {
  key: string
  label: string
  links: MenuLink[]
}

/** 业务模块递给应用壳的菜单分组（由门面 `index.ts` 导出）。 */
export interface FeatureModule {
  name: string
  groups?: MenuGroup[]
}

/** 导航页的一个入口——对应一个应用壳。 */
export interface NavEntry {
  key: string
  label: string
  /** 应用壳路由（如 `/admin`）。 */
  path: string
}
