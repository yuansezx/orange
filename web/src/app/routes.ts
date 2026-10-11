import type { FeatureModule } from '@shared/navigation'

import { homeFeature } from '@features/home'
import { iamFeature } from '@features/iam'

/**
 * 组合根：注册启用的切片——「模块型」对齐后端模块（iam / portal / ...），
 * 「控制台级」不属任何后端模块（home 概览、auth 登录）。新增在此登记。
 */
export const features: FeatureModule[] = [homeFeature, iamFeature]

export const featureRoutes = features.flatMap((feature) => feature.routes)
export const navItems = features.flatMap((feature) => feature.nav ?? [])
