import { Alert, Button, Space, Table, Tooltip } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'
import type { MouseEvent } from 'react'

import { IconEdit, IconTrash } from '@shared/ui'

import { StatusSwitch } from '../../../components/StatusSwitch'
import { USER_TYPE_LABELS } from '../../constants'
import type { UserListItem, UserTableProps, UserType } from '../../types'

/**
 * 【分叉档 · 桌面】—— 宽表格在窄屏不可用，故与移动端拆开。
 * 只负责"渲染 + 分页"，取数在 UserPage；点行看详情，操作列按钮已 stopPropagation。
 */
export function UserTable({
  users,
  loading,
  error,
  total,
  page,
  pageSize,
  onView,
  onEdit,
  onDelete,
  statusPendingId,
  onStatusChange,
  onPageChange,
}: UserTableProps) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const withStop = (handler: () => void) => (event: MouseEvent) => {
    event.stopPropagation()
    handler()
  }

  const columns: TableProps<UserListItem>['columns'] = [
    { title: '用户名', dataIndex: 'username' },
    { title: '昵称', dataIndex: 'nickname' },
    { title: '邮箱', dataIndex: 'email' },
    { title: '手机号', dataIndex: 'phone' },
    {
      title: '类型',
      dataIndex: 'user_type',
      render: (value) => USER_TYPE_LABELS[value as UserType] ?? value,
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (_, record) => (
        <StatusSwitch
          status={record.status}
          loading={statusPendingId === record.id}
          onChange={(status) => onStatusChange(record, status)}
        />
      ),
    },
    {
      title: '创建人',
      key: 'created_by',
      render: (_, record) => record.created_by?.username ?? '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      render: (value) => (value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-'),
    },
    {
      title: '操作',
      width: 120,
      render: (_, record) => (
        <Space size={8}>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<IconEdit size={16} />}
              onClick={withStop(() => onEdit(record))}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<IconTrash size={16} />}
              onClick={withStop(() => onDelete(record))}
            />
          </Tooltip>
        </Space>
      ),
    },
  ]

  return (
    <Table
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={users}
      onRow={(record) => ({ onClick: () => onView(record), style: { cursor: 'pointer' } })}
      pagination={{
        current: page,
        pageSize,
        total,
        showSizeChanger: true,
        showTotal: (count) => `共 ${count} 条`,
        onChange: onPageChange,
      }}
    />
  )
}
