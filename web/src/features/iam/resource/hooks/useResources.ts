import { useQuery } from '@tanstack/react-query'

import { getResources } from '../api/resourceApi'

/** 资源列表用例（无分页；`deleted` = 回收站）。 */
export function useResources(deleted = false, includeDeletedPermissions = false) {
  return useQuery({
    queryKey: ['resources', { deleted, includeDeletedPermissions }],
    queryFn: () =>
      getResources({ deleted, include_deleted_permissions: includeDeletedPermissions }),
  })
}
