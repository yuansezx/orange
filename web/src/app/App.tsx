import { useEffect } from 'react'

import { appConfig } from '@shared/config'

import { AppProviders } from './providers'
import { AppRouter } from './router'

export default function App() {
  useEffect(() => {
    document.title = appConfig.name
  }, [])

  return (
    <AppProviders>
      <AppRouter />
    </AppProviders>
  )
}
