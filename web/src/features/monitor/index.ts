import { createElement, lazy } from 'react'

import type { FeatureModule } from '@shared/navigation'
import { IconFileText } from '@shared/ui'

const AuditLogPage = lazy(() => import('./auditLog/AuditLogPage'))

/** monitor 模块门面：监控分组 + 审计日志入口。 */
export const feature: FeatureModule = {
  name: 'monitor',
  label: '监控',
  icon: createElement(IconFileText, { size: 20 }),
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
  groups: [
    {
      key: 'monitor',
      label: '监控',
      icon: createElement(IconFileText, { size: 16 }),
      links: [
        {
          key: 'monitor-audit-log',
          label: '审计日志',
          path: 'audit-logs',
          permission: 'monitor:audit_log:read',
          icon: createElement(IconFileText, { size: 16 }),
          element: createElement(AuditLogPage),
        },
      ],
    },
  ],
}
