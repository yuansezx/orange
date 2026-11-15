import { get } from '@shared/api'

import type { SystemVersions } from '../types'

const BASE = '/api/monitor/system'

export function getSystemVersions(): Promise<SystemVersions> {
  return get<SystemVersions>(`${BASE}/versions`)
}
