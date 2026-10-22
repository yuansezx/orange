import { Button, ErrorBlock, List, Tag } from 'antd-mobile'
import dayjs from 'dayjs'

import { RESULT_LABELS } from '../../constants'
import type { AuditLogItem } from '../../types'

interface Props {
  logs: AuditLogItem[]
  loading: boolean
  error: Error | null
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number, pageSize: number) => void
  onView: (log: AuditLogItem) => void
}

/** 【分叉档 · 移动】审计日志卡片列表。 */
export function AuditLogCardList({
  logs,
  loading,
  error,
  page,
  pageSize,
  total,
  onPageChange,
  onView,
}: Props) {
  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <div>
      <List>
        {logs.map((log) => (
          <List.Item
            key={log.id}
            description={`${dayjs(log.occurred_at).format('YYYY-MM-DD HH:mm:ss')} · ${log.key}`}
            onClick={() => onView(log)}
          >
            <div style={{ fontWeight: 600 }}>{log.summary}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', marginTop: 4 }}>
              <span style={{ color: '#999' }}>
                操作人：{log.operator_nickname || log.operator_username || '-'}
              </span>
              <Tag color={log.result === 'success' ? 'success' : 'danger'}>
                {RESULT_LABELS[log.result]}
              </Tag>
            </div>
          </List.Item>
        ))}
        {loading && logs.length === 0 && <List.Item>加载中…</List.Item>}
        {!loading && logs.length === 0 && <List.Item>暂无审计日志</List.Item>}
      </List>
      {total > pageSize && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 12,
            padding: 12,
          }}
        >
          <Button
            size="mini"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1, pageSize)}
          >
            上一页
          </Button>
          <span>
            {page} / {Math.max(1, Math.ceil(total / pageSize))}
          </span>
          <Button
            size="mini"
            disabled={page >= Math.ceil(total / pageSize)}
            onClick={() => onPageChange(page + 1, pageSize)}
          >
            下一页
          </Button>
        </div>
      )}
    </div>
  )
}
