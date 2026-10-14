import { createElement } from 'react'

import type { NavEntry } from '@shared/navigation'
import { IconLayoutDashboard } from '@shared/ui'

/** 应用壳（后台管理）的路由基址。 */
export const ADMIN_PATH = '/admin'

/** 导航页的入口列表（控制台级 IA）——每个入口进入一个应用壳。 */
export const navEntries: NavEntry[] = [
  {
    key: 'admin',
    label: '后台管理',
    path: ADMIN_PATH,
    icon: createElement(IconLayoutDashboard, { size: 28 }),
  },
]
