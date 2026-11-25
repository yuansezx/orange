import { get, http, post } from '@shared/api'

import type { AppLogFile, GetAppLogsQuery } from '../types'

const BASE = '/api/monitor/app-logs'

export async function getAppLogs(query: GetAppLogsQuery): Promise<AppLogFile[]> {
  return get<AppLogFile[]>(BASE, query)
}

export async function getAppLogText(key: string): Promise<string> {
  return get<string>(`${BASE}/view`, { key }, { responseType: 'text' })
}

export async function downloadAppLog(key: string): Promise<void> {
  const res = await http.get<Blob>(`${BASE}/download`, {
    params: { key },
    responseType: 'blob',
  })
  const filename = key.split('/').pop() || 'app.log'
  const url = URL.createObjectURL(res.data)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

export async function triggerAppLogArchive(): Promise<void> {
  await post<void>(`${BASE}/archive`)
}
