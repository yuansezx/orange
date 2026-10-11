import { useQuery } from '@tanstack/react-query'

import { getUsers } from '../api/userApi'
import type { GetUsersQuery } from '../types'

/** 用户列表用例（application 层）：服务器状态由 TanStack Query 托管。 */
export function useUsers(query: GetUsersQuery) {
  return useQuery({
    queryKey: ['users', query],
    queryFn: () => getUsers(query),
  })
}
