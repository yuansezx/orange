import { createElement, lazy } from 'react'

import type { FeatureModule } from '@shared/navigation'
import {
  IconBox,
  IconDevices,
  IconShieldLock,
  IconSitemap,
  IconUserCircle,
  IconUsers,
} from '@shared/ui'

const UserPage = lazy(() => import('./user/UserPage'))
const SessionPage = lazy(() => import('./session/SessionPage'))
const RolePage = lazy(() => import('./role/RolePage'))
const DeptPage = lazy(() => import('./dept/DeptPage'))
const ResourcePage = lazy(() => import('./resource/ResourcePage'))
const ProfileSettingsPage = lazy(() => import('./settings/ProfilePage'))
const SecuritySettingsPage = lazy(() => import('./settings/SecurityPage'))
const SessionsSettingsPage = lazy(() => import('./settings/SessionsPage'))

/**
 * iam 模块门面：声明本模块递给应用壳的**菜单分组**（对齐后端 iam 模块）。
 * 菜单项同时承载其路由（相对应用壳的 `path`）；`permission` = 需要的功能权限码。
 * 各页面（user / role / dept / ...）是模块内部结构，外部只见本门面。
 *
 * 导出的名字固定为 `feature`：组合根按此名自动发现模块型切片（见 `app/routes.ts`）。
 */
export const feature: FeatureModule = {
  name: 'iam',
  label: '权限管理',
  icon: createElement(IconShieldLock, { size: 20 }),
  workspace: {
    key: 'admin',
    label: '后台管理',
    basePath: 'admin',
    systemNav: {
      defaultState: 'expanded',
      behavior: 'push',
      allowedStates: ['hidden', 'rail', 'expanded'],
    },
  },
  settings: [
    {
      key: 'iam-account',
      label: '账号与安全',
      links: [
        {
          key: 'iam-account-profile',
          label: '个人资料',
          path: 'profile',
          icon: createElement(IconUserCircle, { size: 16 }),
          element: createElement(ProfileSettingsPage),
        },
        {
          key: 'iam-account-security',
          label: '安全设置',
          path: 'security',
          icon: createElement(IconShieldLock, { size: 16 }),
          element: createElement(SecuritySettingsPage),
        },
        {
          key: 'iam-account-sessions',
          label: '在线设备',
          path: 'sessions',
          icon: createElement(IconDevices, { size: 16 }),
          element: createElement(SessionsSettingsPage),
        },
      ],
    },
  ],
  groups: [
    {
      key: 'iam',
      label: '权限管理',
      icon: createElement(IconShieldLock, { size: 16 }),
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
          key: 'iam-session',
          label: '在线会话',
          path: 'sessions',
          permission: 'iam:current_user:read_sessions',
          icon: createElement(IconDevices, { size: 16 }),
          element: createElement(SessionPage),
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
        {
          key: 'iam-resource',
          label: '资源管理',
          path: 'resources',
          permission: 'iam:resource:read',
          icon: createElement(IconBox, { size: 16 }),
          element: createElement(ResourcePage),
        },
      ],
    },
  ],
}
