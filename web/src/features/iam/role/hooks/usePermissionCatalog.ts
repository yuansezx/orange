import { useQuery } from '@tanstack/react-query'

import { getPermissionCatalog } from '../api/roleApi'

/** 资源/权限目录（权限树数据源）——变动少，缓存久一点。 */
export function usePermissionCatalog() {
  return useQuery({
    queryKey: ['resource-catalog'],
    queryFn: getPermissionCatalog,
    staleTime: 5 * 60_000,
  })
}
