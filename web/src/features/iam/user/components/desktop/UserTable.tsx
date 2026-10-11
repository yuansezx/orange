import { Alert, Table } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'

import { STATUS_LABELS, USER_TYPE_LABELS } from '../../constants'
import type { UserListItem, UserStatus, UserTableProps, UserType } from '../../types'

/**
 * 【分叉档 · 桌面】—— 宽表格在窄屏不可用，故与移动端拆开。
 * 只负责"渲染 + 分页"，取数在 UserPage。
 */
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
    render: (value) => STATUS_LABELS[value as UserStatus] ?? value,
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    render: (value) => (value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-'),
  },
]

export function UserTable({
  users,
  loading,
  error,
  total,
  page,
  pageSize,
  onPageChange,
}: UserTableProps) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }
  return (
    <Table
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={users}
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
