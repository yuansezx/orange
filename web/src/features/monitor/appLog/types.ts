import type { Dayjs } from 'dayjs'

export type AppLogTailFile = 'app' | 'error'

export type AppLogTailStatus = 'idle' | 'connecting' | 'connected' | 'error'

/** 归档日志文件（对象存储里的一个冷文件）。 */
export interface AppLogFile {
  key: string
  filename: string
  instance: string
  log_date: string
  size: number
  last_modified: string
}

export interface GetAppLogsQuery {
  date_from?: string
  date_to?: string
}

export interface AppLogFilters {
  range: [Dayjs, Dayjs] | null
}
