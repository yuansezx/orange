import { useQuery } from '@tanstack/react-query'

import { getPermissions } from '../api/resourceApi'

/** 扁平权限列表用例；`deleted=true` = 权限回收站。 */
export function usePermissions(deleted = false, enabled = true) {
  return useQuery({
    queryKey: ['permissions', { deleted }],
    queryFn: () => getPermissions(deleted),
    enabled,
  })
}
