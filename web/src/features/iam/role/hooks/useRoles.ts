import { useQuery } from '@tanstack/react-query'

import { getRoles } from '../api/roleApi'

/** 角色列表用例（无分页，全量返回）。 */
export function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: getRoles,
  })
}
