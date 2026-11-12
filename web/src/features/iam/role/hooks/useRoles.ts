import { useQuery } from '@tanstack/react-query'

import { getRoles } from '../api/roleApi'
import type { GetRolesQuery } from '../types'

/** 角色列表用例（分页）：筛选/分页/排序参数即查询键。 */
export function useRoles(query: GetRolesQuery) {
  return useQuery({
    queryKey: ['roles', query],
    queryFn: () => getRoles(query),
  })
}
