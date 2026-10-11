import type { FeatureModule } from '@shared/navigation'

import { routes as userRoutes } from './user/routes'

/**
 * iam 模块门面（= 后端 iam 模块）：聚合本模块各页面的路由与导航。
 * 各页面（user / role / dept / ...）是模块内部结构，外部只见本门面。
 */
export const iamFeature: FeatureModule = {
  name: 'iam',
  routes: [...userRoutes],
  nav: [{ key: 'iam-user', label: '用户', path: '/users' }],
}
