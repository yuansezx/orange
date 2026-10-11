import { Alert, Table } from 'antd'
import type { TableProps } from 'antd'

import type { UserListItem, UserListViewProps } from '../../types'

/**
 * 【分叉档 · 桌面】—— 宽表格在窄屏不可用，故与移动端拆开。
 * 只负责"渲染"，取数不在这里（在 UserPage 一次取好、两端共用）。
 * 同目录的 desktop/ 与 mobile/ 两两成对，代表"同一处的两种形态"。
 */
const columns: TableProps<UserListItem>['columns'] = [
  { title: '用户名', dataIndex: 'username' },
  { title: '昵称', dataIndex: 'nickname' },
  { title: '邮箱', dataIndex: 'email' },
  { title: '手机号', dataIndex: 'phone' },
  { title: '类型', dataIndex: 'user_type' },
  { title: '状态', dataIndex: 'status' },
]

export function UserTable({ users, loading, error }: UserListViewProps) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }
  return <Table rowKey="id" loading={loading} columns={columns} dataSource={users} />
}
