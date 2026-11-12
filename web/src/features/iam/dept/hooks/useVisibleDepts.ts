import { useQuery } from '@tanstack/react-query'

import { getVisibleDepts } from '../api/deptApi'

/** 当前用户可见部门（精简树）：登录即可，按数据范围过滤；各类选择器共用。 */
export function useVisibleDepts() {
  return useQuery({
    queryKey: ['dept-visible'],
    queryFn: getVisibleDepts,
    staleTime: 5 * 60_000,
  })
}
