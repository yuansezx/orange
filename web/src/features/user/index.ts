import type { FeatureModule } from '@shared/navigation'

import { routes } from './routes'

/** 门面：组合根只认这里暴露的契约。 */
export const userFeature: FeatureModule = {
  name: 'user',
  routes,
  nav: [{ key: 'user', label: '用户', path: '/users' }],
}
