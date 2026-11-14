import { useQuery } from '@tanstack/react-query'

import { getSystemVersions } from '../api/systemApi'

/** 版本随构建/部署变化，无需频繁刷新。 */
export function useSystemVersions() {
  return useQuery({
    queryKey: ['system-versions'],
    queryFn: getSystemVersions,
    staleTime: 5 * 60 * 1000,
  })
}
