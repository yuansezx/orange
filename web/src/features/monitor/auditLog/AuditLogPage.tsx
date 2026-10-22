import { useMemo, useState } from 'react'

import { Platform } from '@shared/platform'

import { AuditLogDetailDrawer } from './components/AuditLogDetailDrawer'
import { AuditLogToolbar } from './components/AuditLogToolbar'
import { AuditLogTable } from './components/desktop/AuditLogTable'
import { AuditLogCardList } from './components/mobile/AuditLogCardList'
import { useAuditLogs } from './hooks/useAuditLogs'
import type { AuditLogFilters, AuditLogItem, GetAuditLogsQuery } from './types'

const EMPTY_FILTERS: AuditLogFilters = {
  module: '',
  resource: '',
  action: '',
  result: undefined,
  range: null,
}

/** 审计日志查询页：筛选 + 服务端分页 + 详情。 */
export default function AuditLogPage() {
  const [filters, setFilters] = useState<AuditLogFilters>(EMPTY_FILTERS)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [selected, setSelected] = useState<AuditLogItem | null>(null)

  const query = useMemo<GetAuditLogsQuery>(() => ({
    page,
    page_size: pageSize,
    module: filters.module.trim() || undefined,
    resource: filters.resource.trim() || undefined,
    action: filters.action.trim() || undefined,
    result: filters.result,
    occurred_from: filters.range?.[0]?.toISOString(),
    occurred_to: filters.range?.[1]?.toISOString(),
  }), [filters, page, pageSize])

  const { data, isFetching, error } = useAuditLogs(query)
  const logs = data?.data ?? []
  const total = data?.total ?? 0

  const changeFilters = (value: AuditLogFilters) => {
    setFilters(value)
    setPage(1)
  }

  const changePage = (nextPage: number, nextPageSize: number) => {
    setPage(nextPage)
    setPageSize(nextPageSize)
  }

  const reset = () => {
    setFilters(EMPTY_FILTERS)
    setPage(1)
  }

  const viewProps = {
    logs,
    loading: isFetching,
    error,
    page,
    pageSize,
    total,
    onPageChange: changePage,
    onView: setSelected,
  }

  return (
    <div>
      <AuditLogToolbar value={filters} onChange={changeFilters} onReset={reset} />
      <Platform
        desktop={<AuditLogTable {...viewProps} />}
        mobile={<AuditLogCardList {...viewProps} />}
      />
      <AuditLogDetailDrawer
        open={selected !== null}
        log={selected}
        onClose={() => setSelected(null)}
      />
    </div>
  )
}
