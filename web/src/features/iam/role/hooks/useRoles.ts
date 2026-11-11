import { useQuery } from '@tanstack/react-query'

import { getRoles } from '../api/roleApi'
import type { GetRolesQuery } from '../types'

interface UseRolesOptions extends GetRolesQuery {
  /** 按需取数（如仅在创建用户时才拉角色）。 */
  enabled?: boolean
}

/** 角色列表用例（无分页，全量返回；`deleted` = 回收站）。 */
export function useRoles({
  deleted = false,
  sort_by = 'code',
  order = 'asc',
  enabled = true,
}: UseRolesOptions = {}) {
  return useQuery({
    queryKey: ['roles', { deleted, sort_by, order }],
    queryFn: () => getRoles({ deleted: deleted || undefined, sort_by, order }),
    enabled,
  })
}
