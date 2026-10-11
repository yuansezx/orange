import { iamFeature } from '@features/iam'
import type { FeatureModule, MenuGroup, MenuLink } from '@shared/navigation'

/** 组合根：注册启用的业务模块（对齐后端模块）。新增在此登记。 */
export const features: FeatureModule[] = [iamFeature]

/** 应用壳的菜单分组（聚合各 feature 门面导出的 groups）。 */
export const menuGroups: MenuGroup[] = features.flatMap((feature) => feature.groups ?? [])

/** 拉平后的菜单项——应用壳据此生成路由（应用壳在 `app/router.tsx`）。 */
export const menuLinks: MenuLink[] = menuGroups.flatMap((group) => group.links)
