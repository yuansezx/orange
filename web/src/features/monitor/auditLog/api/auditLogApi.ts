import { get } from '@shared/api'
import type { PageResult } from '@shared/api'

import type { AuditLogItem, GetAuditLogsQuery } from '../types'

const BASE = '/api/monitor/audit-logs'

export async function getAuditLogs(
  query: GetAuditLogsQuery,
): Promise<PageResult<AuditLogItem>> {
  const page = await get<PageResult<AuditLogItem>>(BASE, query)
  return { ...page, data: page.data ?? [] }
}
