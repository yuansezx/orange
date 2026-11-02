import { useMe } from './useMe'

/**
 * 功能权限判定——复刻后端语义：**超管旁路**（`super_admin` 恒通过），否则看 `permission_codes`。
 * 码缺省 / 空串 = 永远可见。菜单按此过滤（数据权限不在此列）。
 */
export function usePermission() {
  const { data: me } = useMe()

  const can = (code?: string): boolean => {
    if (!code) return true
    if (!me) return false
    if (me.user_type === 'super_admin') return true
    return (me.permission_codes ?? []).includes(code)
  }

  return { can, me }
}
