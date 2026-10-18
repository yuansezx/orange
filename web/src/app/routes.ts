import type { FeatureModule, MenuGroup, MenuLink } from '@shared/navigation'

/**
 * 组合根：**构建期发现**模块型切片——扫描 `features/<module>/index.ts`，取门面导出的 `feature`。
 *
 * 用 glob 而非硬编码清单：目录不存在即跳过。这样开源仓缺少闭源模块时不会出现
 * 指向不存在目录的 import，新增模块也不必回来登记。控制台级切片（如 auth）
 * 不导出 `feature`，自然不进入本表。
 *
 * 运行时不做模块开关：可见性由后端权限码过滤菜单承担，前端不再放第二份「启用清单」。
 */
const discovered = import.meta.glob<{ feature?: FeatureModule }>('../features/*/index.ts', {
  eager: true,
})

export const features: FeatureModule[] = Object.keys(discovered)
  .sort()
  .map((path) => discovered[path].feature)
  .filter((feature): feature is FeatureModule => feature !== undefined)

/** 应用壳的菜单分组（聚合各 feature 门面导出的 groups）。 */
export const menuGroups: MenuGroup[] = features.flatMap((feature) => feature.groups ?? [])

/** 拉平后的菜单项——应用壳据此生成路由（应用壳在 `app/router.tsx`）。 */
export const menuLinks: MenuLink[] = menuGroups.flatMap((group) => group.links)
