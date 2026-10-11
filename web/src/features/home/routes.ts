import { createElement, lazy } from 'react'

import type { FeatureRoute } from '@shared/navigation'

const HomePage = lazy(() => import('./HomePage'))

export const routes: FeatureRoute[] = [{ path: '/home', element: createElement(HomePage) }]
