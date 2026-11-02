/**
 * 在当前 `pathname` 下命中哪条菜单项——**精确**匹配 `/{fullPath}`，
 * 或 `/{fullPath}/**`（兼容将来的子路由，如详情页）。
 */
export function matchNavLink<T extends { fullPath: string }>(
  links: T[],
  pathname: string,
): T | undefined {
  return links.find((link) => {
    const full = `/${link.fullPath}`
    return pathname === full || pathname.startsWith(`${full}/`)
  })
}
