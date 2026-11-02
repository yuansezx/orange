import { QueryClient } from '@tanstack/react-query'

/** 全局 QueryClient：服务器状态（API 数据）统一在此缓存 / 失效 / 重试。 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

/** queryKey 约定：按 feature 前缀，避免跨模块撞键。 */
export const queryKeys = {
  me: ['me'] as const,
}
