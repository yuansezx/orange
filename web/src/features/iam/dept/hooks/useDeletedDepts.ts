import { useQuery } from '@tanstack/react-query'

import { getDepts } from '../api/deptApi'

/** 回收站扁平列表（含审计）——仅在回收站模式启用。 */
export function useDeletedDepts(enabled: boolean) {
  return useQuery({
    queryKey: ['depts', { deleted: true }],
    queryFn: () => getDepts({ deleted: true }),
    enabled,
  })
}
