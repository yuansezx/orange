import { createElement, lazy } from 'react'

import type { FeatureRoute } from '@shared/navigation'

const UserPage = lazy(() => import('./UserPage'))

export const routes: FeatureRoute[] = [{ path: '/users', element: createElement(UserPage) }]
