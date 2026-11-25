import { useMutation, useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'

import { isApiError } from '@shared/api'

import { triggerAppLogArchive } from '../api/appLogApi'

/** 手动触发一次日志归档（命令，不是事件）。 */
export function useAppLogArchive() {
  const { message } = App.useApp()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: triggerAppLogArchive,
    onSuccess: () => {
      message.success('已触发归档')
      // 归档任务是异步的，稍后再刷新列表
      window.setTimeout(() => {
        void queryClient.invalidateQueries({ queryKey: ['app-logs'] })
      }, 1500)
    },
    onError: (error) => {
      message.error(isApiError(error) ? error.message : '触发失败，请重试')
    },
  })
}
