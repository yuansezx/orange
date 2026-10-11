import type { ReactNode } from 'react'

/** 一条路由（由各 feature 自声明，组合根聚合）。 */
export interface FeatureRoute {
  path: string
  element: ReactNode
}

/** 一条导航（菜单 / TabBar 项）。 */
export interface NavItem {
  key: string
  label: string
  path: string
  icon?: ReactNode
}

/**
 * 业务模块对外契约——对应后端的「模块暴露 router」。
 * feature 只在门面 `index.ts` 导出它，组合根据此聚合路由与导航。
 */
export interface FeatureModule {
  name: string
  routes: FeatureRoute[]
  nav?: NavItem[]
}
