import { useQuery } from '@tanstack/react-query'

import { getToken } from '@shared/auth/token'

import { getMe } from '../api/authApi'

/**
 * 当前用户（服务器状态）——`/api/iam/users/me`。
 * 未登录（无令牌）不发请求；导航页按 `permission_codes` 过滤菜单时会用到。
 */
export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: getMe,
    enabled: getToken() !== null,
    staleTime: 5 * 60_000,
  })
}
