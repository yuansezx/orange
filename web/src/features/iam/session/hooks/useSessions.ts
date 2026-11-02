import { useQuery } from '@tanstack/react-query'

import { getSessions } from '../api/sessionApi'

/** 在线会话列表用例（不分页）：服务器状态由 TanStack Query 托管。 */
export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
  })
}
