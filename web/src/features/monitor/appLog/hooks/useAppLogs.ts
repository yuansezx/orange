import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { getAppLogs } from '../api/appLogApi'
import type { GetAppLogsQuery } from '../types'

/** 归档日志列表：服务器状态由 TanStack Query 托管。 */
export function useAppLogs(query: GetAppLogsQuery) {
  return useQuery({
    queryKey: ['app-logs', query],
    queryFn: () => getAppLogs(query),
    placeholderData: keepPreviousData,
  })
}
