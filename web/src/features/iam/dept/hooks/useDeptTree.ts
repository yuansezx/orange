import { useQuery } from '@tanstack/react-query'

import { getDeptTree } from '../api/deptApi'

/** 部门树用例：服务器状态由 TanStack Query 托管（写操作后 invalidate 该键）。 */
export function useDeptTree() {
  return useQuery({
    queryKey: ['dept-tree'],
    queryFn: getDeptTree,
  })
}
