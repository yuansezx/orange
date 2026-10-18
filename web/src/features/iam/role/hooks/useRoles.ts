import { useQuery } from '@tanstack/react-query'

import { getRoles } from '../api/roleApi'

/** 角色列表用例（无分页，全量返回；`deleted` = 回收站）。 */
export function useRoles(deleted = false) {
  return useQuery({
    queryKey: ['roles', { deleted }],
    queryFn: () => getRoles(deleted),
  })
}
