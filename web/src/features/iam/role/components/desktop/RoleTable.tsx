import { Alert, Button, Space, Table, Tag, Tooltip } from 'antd'
import type { TableProps } from 'antd'

import { IconEdit, IconTrash } from '@shared/ui'

import { DATA_SCOPE_LABELS, STATUS_COLORS, STATUS_LABELS } from '../../../constants'
import type { Role } from '../../types'

interface Props {
  roles: Role[]
  loading: boolean
  error: Error | null
  onEdit: (role: Role) => void
  onDelete: (role: Role) => void
}

/** 【分叉档 · 桌面】角色表格；只负责渲染 + 操作回调，取数与弹层在 RolePage。 */
export function RoleTable({ roles, loading, error, onEdit, onDelete }: Props) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const columns: TableProps<Role>['columns'] = [
    { title: '角色标识', dataIndex: 'code', width: 200 },
    { title: '名称', dataIndex: 'name', width: 200 },
    {
      title: '数据范围',
      dataIndex: 'data_scope',
      width: 130,
      render: (value: Role['data_scope']) => DATA_SCOPE_LABELS[value],
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (value: Role['status']) => (
        <Tag color={STATUS_COLORS[value]}>{STATUS_LABELS[value]}</Tag>
      ),
    },
    { title: '描述', dataIndex: 'description', ellipsis: true },
    {
      title: '操作',
      width: 120,
      render: (_, record) => (
        <Space size={8}>
          <Tooltip title="编辑">
            <Button type="text" icon={<IconEdit size={16} />} onClick={() => onEdit(record)} />
          </Tooltip>
          <Tooltip title="删除">
            <Button type="text" danger icon={<IconTrash size={16} />} onClick={() => onDelete(record)} />
          </Tooltip>
        </Space>
      ),
    },
  ]

  return (
    <Table<Role> rowKey="id" loading={loading} columns={columns} dataSource={roles} pagination={false} />
  )
}
