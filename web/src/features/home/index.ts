import type { FeatureModule } from '@shared/navigation'

import { routes } from './routes'

/** 门面：组合根只认这里暴露的契约。 */
export const homeFeature: FeatureModule = {
  name: 'home',
  routes,
  nav: [{ key: 'home', label: '概览', path: '/home' }],
}
