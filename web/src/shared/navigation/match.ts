import type { MenuLink } from './types'

/**
 * 在当前 `pathname` 下命中哪条菜单项——**精确**匹配 `{basePath}/{link.path}`，
 * 或 `{basePath}/{link.path}/**`（兼容将来的子路由，如详情页）。
 */
export function matchMenuLink(
  links: MenuLink[],
  pathname: string,
  basePath: string,
): MenuLink | undefined {
  return links.find((link) => {
    const base = `${basePath}/${link.path}`
    return pathname === base || pathname.startsWith(`${base}/`)
  })
}
