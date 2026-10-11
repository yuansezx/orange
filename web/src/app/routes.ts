import type { FeatureModule } from '@shared/navigation'

import { homeFeature } from '@features/home'
import { userFeature } from '@features/user'

/** 组合根：注册启用的业务模块（对应后端 core.modules）。新增模块在此登记。 */
export const features: FeatureModule[] = [homeFeature, userFeature]

export const featureRoutes = features.flatMap((feature) => feature.routes)
export const navItems = features.flatMap((feature) => feature.nav ?? [])
