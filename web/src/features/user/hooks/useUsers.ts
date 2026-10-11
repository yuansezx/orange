import { useQuery } from '@tanstack/react-query'

import { USE_MOCK } from '@shared/lib/env'

import { getUsers } from '../api/userApi'
import { MOCK_USERS } from '../mock'
import type { GetUsersQuery } from '../types'

/** 用户列表用例（application 层）：服务器状态由 TanStack Query 托管。 */
export function useUsers(query: GetUsersQuery) {
  return useQuery({
    queryKey: ['users', query],
    queryFn: () => {
      if (USE_MOCK) {
        return Promise.resolve({
          page: query.page ?? 1,
          page_size: query.page_size ?? 10,
          total: MOCK_USERS.length,
          total_pages: 1,
          data: MOCK_USERS,
        })
      }
      return getUsers(query)
    },
  })
}
