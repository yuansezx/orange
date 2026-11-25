import { useQuery } from '@tanstack/react-query'

import { getAppLogText } from '../api/appLogApi'

/** 单个归档日志的文本内容（查看抽屉用）。 */
export function useAppLogText(key: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ['app-log-text', key],
    queryFn: () => getAppLogText(key as string),
    enabled: enabled && !!key,
  })
}
