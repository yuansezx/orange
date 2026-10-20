import { Alert, Button, Space, Table, Tag, Tooltip } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'

import { IconRestore, IconTrashX } from '@shared/ui'

import { SOURCE_COLORS, SOURCE_LABELS } from '../../constants'
import type { PermissionListItem } from '../../types'

interface Props {
  permissions: PermissionListItem[]
  loading: boolean
  error: Error | null
  onRestore: (permission: PermissionListItem) => void
  onHardDelete: (permission: PermissionListItem) => void
}

/** 【分叉档 · 桌面】权限回收站：资源仍存活的已删权限（随资源删的不在此列）。 */
export function DeletedPermissionTable({
  permissions,
  loading,
  error,
  onRestore,
  onHardDelete,
}: Props) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const columns: TableProps<PermissionListItem>['columns'] = [
    {
      title: '所属资源',
      key: 'resource',
      width: 220,
      render: (_, record) => (
        <div>
          <div>{record.resource_name}</div>
          <div style={{ color: '#999', fontSize: 12 }}>{record.resource_key}</div>
        </div>
      ),
    },
    { title: '动作', dataIndex: 'action', width: 160 },
    { title: '名称', dataIndex: 'name', width: 180 },
    { title: '完整标识', dataIndex: 'key', ellipsis: true },
    {
      title: '来源',
      dataIndex: 'permission_type',
      width: 90,
      render: (value: PermissionListItem['permission_type']) => (
        <Tag color={SOURCE_COLORS[value]}>{SOURCE_LABELS[value]}</Tag>
      ),
    },
    {
      title: '删除时间',
      dataIndex: 'deleted_at',
      width: 170,
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
      render: (_, record) => {
        if (record.permission_type === 'system') {
          return <span style={{ color: '#999' }}>代码维护</span>
        }
        return (
          <Space size={8}>
            <Tooltip title="恢复">
              <Button
                type="text"
                icon={<IconRestore size={16} />}
                onClick={() => onRestore(record)}
              />
            </Tooltip>
            <Tooltip title="彻底删除">
              <Button
                type="text"
                danger
                icon={<IconTrashX size={16} />}
                onClick={() => onHardDelete(record)}
              />
            </Tooltip>
          </Space>
        )
      },
    },
  ]

  return (
    <Table<PermissionListItem>
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={permissions}
      pagination={false}
    />
  )
}
