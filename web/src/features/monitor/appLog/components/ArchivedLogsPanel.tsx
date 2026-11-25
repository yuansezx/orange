import { useState } from 'react'

import { App } from 'antd'

import { isApiError } from '@shared/api'
import { Platform } from '@shared/platform'

import { downloadAppLog } from '../api/appLogApi'
import { useAppLogs } from '../hooks/useAppLogs'
import type { AppLogFile, AppLogFilters, GetAppLogsQuery } from '../types'
import { AppLogToolbar } from './AppLogToolbar'
import { AppLogViewerDrawer } from './AppLogViewerDrawer'
import { AppLogTable } from './desktop/AppLogTable'
import { AppLogCardList } from './mobile/AppLogCardList'

const EMPTY_FILTERS: AppLogFilters = { range: null }

/** 归档日志：日期筛选 + 列表 + 查看 / 下载 + 手动归档。 */
export function ArchivedLogsPanel() {
  const { message } = App.useApp()
  const [filters, setFilters] = useState<AppLogFilters>(EMPTY_FILTERS)
  const [selected, setSelected] = useState<AppLogFile | null>(null)

  const query: GetAppLogsQuery = {
    date_from: filters.range?.[0]?.format('YYYY-MM-DD'),
    date_to: filters.range?.[1]?.format('YYYY-MM-DD'),
  }
  const { data, isFetching, error, refetch } = useAppLogs(query)
  const files = data ?? []

  const handleDownload = async (file: AppLogFile) => {
    try {
      await downloadAppLog(file.key)
    } catch (err) {
      message.error(isApiError(err) ? err.message : '下载失败，请重试')
    }
  }

  const viewProps = {
    files,
    loading: isFetching,
    error: error ?? null,
    onView: setSelected,
    onDownload: handleDownload,
  }

  return (
    <div>
      <AppLogToolbar
        value={filters}
        onChange={setFilters}
        onRefresh={() => void refetch()}
        refreshing={isFetching}
      />
      <Platform
        desktop={<AppLogTable {...viewProps} />}
        mobile={<AppLogCardList {...viewProps} />}
      />
      <AppLogViewerDrawer
        open={selected !== null}
        file={selected}
        onClose={() => setSelected(null)}
      />
    </div>
  )
}
