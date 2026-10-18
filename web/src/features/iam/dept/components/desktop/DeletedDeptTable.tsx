import { Alert, Button, Space, Table, Tag, Tooltip } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'
import type { MouseEvent } from 'react'

import { IconRestore, IconTrashX } from '@shared/ui'

import { STATUS_COLORS, STATUS_LABELS } from '../../../constants'
import type { DeptListItem } from '../../types'

interface Props {
  depts: DeptListItem[]
  loading: boolean
  error: Error | null
  onView: (dept: DeptListItem) => void
  onRestore: (dept: DeptListItem) => void
  onHardDelete: (dept: DeptListItem) => void
}

/** 【分叉档 · 桌面】回收站扁平表格：已删部门 + 恢复 / 彻底删除。 */
export function DeletedDeptTable({ depts, loading, error, onView, onRestore, onHardDelete }: Props) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const withStop = (handler: () => void) => (event: MouseEvent) => {
    event.stopPropagation()
    handler()
  }

  const columns: TableProps<DeptListItem>['columns'] = [
    { title: '部门名称', dataIndex: 'name', ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (value: DeptListItem['status']) => (
        <Tag color={STATUS_COLORS[value]}>{STATUS_LABELS[value]}</Tag>
      ),
    },
    {
      title: '删除时间',
      dataIndex: 'deleted_at',
      width: 180,
      render: (value: string | null) =>
        value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '删除人',
      key: 'deleted_by',
      width: 120,
      render: (_, record) => record.deleted_by?.username ?? '-',
    },
    {
      title: '操作',
      width: 100,
      render: (_, record) => (
        <Space size={8}>
          <Tooltip title="恢复">
            <Button
              type="text"
              icon={<IconRestore size={16} />}
              onClick={withStop(() => onRestore(record))}
            />
          </Tooltip>
          <Tooltip title="彻底删除">
            <Button
              type="text"
              danger
              icon={<IconTrashX size={16} />}
              onClick={withStop(() => onHardDelete(record))}
            />
          </Tooltip>
        </Space>
      ),
    },
  ]

  return (
    <Table<DeptListItem>
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={depts}
      pagination={false}
      onRow={(record) => ({ onClick: () => onView(record), style: { cursor: 'pointer' } })}
    />
  )
}
