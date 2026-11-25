import { createElement, lazy } from 'react'

import type { FeatureModule } from '@shared/navigation'
import { IconFileText, IconInfoCircle, IconTerminal2 } from '@shared/ui'

const AppLogPage = lazy(() => import('./appLog/AppLogPage'))
const AuditLogPage = lazy(() => import('./auditLog/AuditLogPage'))
const SystemInfoPage = lazy(() => import('./system/SystemInfoPage'))

/** monitor 模块门面：向后台管理贡献监控分组 + 审计日志入口。 */
export const feature: FeatureModule = {
  name: 'monitor',
  label: '监控',
  icon: createElement(IconFileText, { size: 20 }),
  // 后台技术管理页的标准写法：用 `admin` 通道贡献到平台统一的 ADMIN_WORKSPACE。
  admin: [
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
        {
          key: 'monitor-app-log',
          label: '应用日志',
          path: 'app-logs',
          permission: 'monitor:app_log:read',
          icon: createElement(IconTerminal2, { size: 16 }),
          element: createElement(AppLogPage),
        },
        {
          key: 'monitor-system',
          label: '版本信息',
          path: 'system',
          permission: 'monitor:system:read',
          icon: createElement(IconInfoCircle, { size: 16 }),
          element: createElement(SystemInfoPage),
        },
      ],
    },
  ],
}
