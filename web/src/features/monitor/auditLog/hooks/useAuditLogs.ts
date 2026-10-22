import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { getAuditLogs } from '../api/auditLogApi'
import type { GetAuditLogsQuery } from '../types'

/** 审计日志列表用例：服务器状态由 TanStack Query 托管。 */
export function useAuditLogs(query: GetAuditLogsQuery) {
  return useQuery({
    queryKey: ['audit-logs', query],
    queryFn: () => getAuditLogs(query),
    placeholderData: keepPreviousData,
  })
}
