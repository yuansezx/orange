import { Alert, Button, Space, Table, Tag, Tooltip } from 'antd'
import type { TableProps } from 'antd'
import type { MouseEvent } from 'react'

import { IconEdit, IconTrash } from '@shared/ui'

import { DATA_SCOPE_LABELS, STATUS_COLORS, STATUS_LABELS } from '../../../constants'
import type { RoleListItem } from '../../types'

interface Props {
  roles: RoleListItem[]
  loading: boolean
  error: Error | null
  onView: (role: RoleListItem) => void
  onEdit: (role: RoleListItem) => void
  onDelete: (role: RoleListItem) => void
}

/** 【分叉档 · 桌面】角色表格：**点行看详情**，操作列按钮已 stopPropagation；取数与弹层在 RolePage。 */
export function RoleTable({ roles, loading, error, onView, onEdit, onDelete }: Props) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  // 操作按钮点击不应冒泡到行（否则会同时打开详情）
  const withStop = (handler: () => void) => (event: MouseEvent) => {
    event.stopPropagation()
    handler()
  }

  const columns: TableProps<RoleListItem>['columns'] = [
    { title: '角色标识', dataIndex: 'code', width: 200 },
    { title: '名称', dataIndex: 'name', width: 200 },
    {
      title: '数据范围',
      dataIndex: 'data_scope',
      width: 130,
      render: (value: RoleListItem['data_scope']) => DATA_SCOPE_LABELS[value],
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (value: RoleListItem['status']) => (
        <Tag color={STATUS_COLORS[value]}>{STATUS_LABELS[value]}</Tag>
      ),
    },
    { title: '描述', dataIndex: 'description', ellipsis: true },
    {
      title: '创建人',
      key: 'created_by',
      width: 120,
      render: (_, record) => record.created_by?.username ?? '-',
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
    <Table<RoleListItem>
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={roles}
      pagination={false}
      onRow={(record) => ({ onClick: () => onView(record), style: { cursor: 'pointer' } })}
    />
  )
}
