import { createElement, lazy } from 'react'

import type { FeatureModule } from '@shared/navigation'
import { IconShieldLock, IconSitemap, IconUsers } from '@shared/ui'

const UserPage = lazy(() => import('./user/UserPage'))
const RolePage = lazy(() => import('./role/RolePage'))
const DeptPage = lazy(() => import('./dept/DeptPage'))

/**
 * iam 模块门面：声明本模块递给应用壳的**菜单分组**（对齐后端 iam 模块）。
 * 菜单项同时承载其路由（相对应用壳的 `path`）；`permission` = 需要的功能权限码。
 * 各页面（user / role / dept / ...）是模块内部结构，外部只见本门面。
 */
export const iamFeature: FeatureModule = {
  name: 'iam',
  groups: [
    {
      key: 'iam',
      label: '权限管理',
      links: [
        {
          key: 'iam-user',
          label: '用户管理',
          path: 'users',
          permission: 'iam:user:read',
          icon: createElement(IconUsers, { size: 16 }),
          element: createElement(UserPage),
        },
        {
          key: 'iam-role',
          label: '角色管理',
          path: 'roles',
          permission: 'iam:role:read',
          icon: createElement(IconShieldLock, { size: 16 }),
          element: createElement(RolePage),
        },
        {
          key: 'iam-dept',
          label: '部门管理',
          path: 'depts',
          permission: 'iam:dept:read',
          icon: createElement(IconSitemap, { size: 16 }),
          element: createElement(DeptPage),
        },
      ],
    },
  ],
}
