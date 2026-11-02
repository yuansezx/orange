import { Alert, Table, Tag } from 'antd'
import type { TableProps } from 'antd'
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

/** 【分叉档 · 桌面】审计日志表格：点行看详情。 */
export function AuditLogTable({
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
    return <Alert type="error" message={error.message} showIcon />
  }

  const columns: TableProps<AuditLogItem>['columns'] = [
    {
      title: '时间',
      dataIndex: 'occurred_at',
      width: 170,
      render: (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm:ss'),
    },
    { title: '动作码', dataIndex: 'key', width: 190 },
    { title: '摘要', dataIndex: 'summary', ellipsis: true },
    {
      title: '操作人',
      key: 'operator',
      width: 130,
      render: (_, record) => record.operator_nickname || record.operator_username || '-',
    },
    {
      title: '目标',
      key: 'target',
      width: 160,
      ellipsis: true,
      render: (_, record) => record.target_name || record.target_id || '-',
    },
    {
      title: '结果',
      dataIndex: 'result',
      width: 90,
      render: (value: AuditLogItem['result']) => (
        <Tag color={value === 'success' ? 'success' : 'error'}>
          {RESULT_LABELS[value]}
        </Tag>
      ),
    },
    { title: 'IP', dataIndex: 'ip', width: 130 },
  ]

  return (
    <Table<AuditLogItem>
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={logs}
      onRow={(record) => ({
        onClick: () => onView(record),
        style: { cursor: 'pointer' },
      })}
      pagination={{
        current: page,
        pageSize,
        total,
        showSizeChanger: true,
        pageSizeOptions: [20, 50, 100],
        onChange: onPageChange,
      }}
    />
  )
}
