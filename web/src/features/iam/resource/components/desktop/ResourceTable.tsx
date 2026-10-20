import { Alert, Button, Space, Table, Tag, Tooltip } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'

import { IconEdit, IconRestore, IconTrash, IconTrashX } from '@shared/ui'

import { StatusSwitch } from '../../../components/StatusSwitch'
import { STATUS_LABELS } from '../../../constants'
import type { Status } from '../../../types'
import { SOURCE_COLORS, SOURCE_LABELS } from '../../constants'
import type { Resource, ResourcePermission } from '../../types'

interface PermissionTableProps {
  resource: Resource
  recycleMode: boolean
  statusPendingId?: string
  onCreate: (resource: Resource) => void
  onEdit: (resource: Resource, permission: ResourcePermission) => void
  onDelete: (resource: Resource, permission: ResourcePermission) => void
  onStatusChange: (resource: Resource, permission: ResourcePermission, status: Status) => void
}

/** 资源展开区：聚合内权限列表（SYSTEM 只读；CUSTOM 可增删改）。 */
function PermissionTable({
  resource,
  recycleMode,
  statusPendingId,
  onCreate,
  onEdit,
  onDelete,
  onStatusChange,
}: PermissionTableProps) {
  const columns: TableProps<ResourcePermission>['columns'] = [
    { title: '动作', dataIndex: 'action', width: 160 },
    { title: '名称', dataIndex: 'name', width: 160 },
    { title: '完整标识', dataIndex: 'key', ellipsis: true },
    {
      title: '来源',
      dataIndex: 'permission_type',
      width: 90,
      render: (value: ResourcePermission['permission_type']) => (
        <Tag color={SOURCE_COLORS[value]}>{SOURCE_LABELS[value]}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 120,
      render: (_, permission) => {
        if (permission.deleted_at) {
          return <Tag>已删除</Tag>
        }
        if (permission.permission_type === 'system') {
          return <Tag>{STATUS_LABELS[permission.status]}</Tag>
        }
        return (
          <StatusSwitch
            status={permission.status}
            disabled={recycleMode}
            loading={statusPendingId === permission.id}
            onChange={(status) => onStatusChange(resource, permission, status)}
          />
        )
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 170,
      render: (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      width: 120,
      render: (_, permission) => {
        if (recycleMode) {
          return <span style={{ color: '#999' }}>-</span>
        }
        if (permission.permission_type === 'system') {
          return <span style={{ color: '#999' }}>代码维护</span>
        }
        return (
          <Space size={8}>
            <Tooltip title="编辑">
              <Button
                type="text"
                icon={<IconEdit size={16} />}
                onClick={() => onEdit(resource, permission)}
              />
            </Tooltip>
            <Tooltip title="删除">
              <Button
                type="text"
                danger
                icon={<IconTrash size={16} />}
                onClick={() => onDelete(resource, permission)}
              />
            </Tooltip>
          </Space>
        )
      },
    },
  ]

  return (
    <div>
      {!recycleMode && (
        <Space style={{ marginBottom: 8 }}>
          <Button size="small" onClick={() => onCreate(resource)}>
            新增权限
          </Button>
        </Space>
      )}
      <Table<ResourcePermission>
        rowKey="id"
        size="small"
        pagination={false}
        columns={columns}
        dataSource={resource.permissions}
        locale={{ emptyText: '暂无权限' }}
      />
    </div>
  )
}

interface Props {
  resources: Resource[]
  loading: boolean
  error: Error | null
  recycleMode: boolean
  statusPendingId?: string
  permissionStatusPendingId?: string
  onEdit: (resource: Resource) => void
  onDelete: (resource: Resource) => void
  onRestore: (resource: Resource) => void
  onHardDelete: (resource: Resource) => void
  onStatusChange: (resource: Resource, status: Status) => void
  onCreatePermission: (resource: Resource) => void
  onEditPermission: (resource: Resource, permission: ResourcePermission) => void
  onDeletePermission: (resource: Resource, permission: ResourcePermission) => void
  onPermissionStatusChange: (
    resource: Resource,
    permission: ResourcePermission,
    status: Status,
  ) => void
}

/** 【分叉档 · 桌面】资源表格：行内展开权限；STATUS/来源决定可操作项。 */
export function ResourceTable({
  resources,
  loading,
  error,
  recycleMode,
  statusPendingId,
  permissionStatusPendingId,
  onEdit,
  onDelete,
  onRestore,
  onHardDelete,
  onStatusChange,
  onCreatePermission,
  onEditPermission,
  onDeletePermission,
  onPermissionStatusChange,
}: Props) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const recycleColumns: NonNullable<TableProps<Resource>['columns']> = recycleMode
    ? [
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
      ]
    : []

  const columns: TableProps<Resource>['columns'] = [
    { title: '模块', dataIndex: 'module', width: 100 },
    { title: '资源标识', dataIndex: 'code', width: 160 },
    { title: '名称', dataIndex: 'name', width: 160 },
    {
      title: '来源',
      dataIndex: 'resource_type',
      width: 90,
      render: (value: Resource['resource_type']) => (
        <Tag color={SOURCE_COLORS[value]}>{SOURCE_LABELS[value]}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (_, record) => (
        <StatusSwitch
          status={record.status}
          disabled={recycleMode || record.resource_type === 'system'}
          disabledReason={
            record.resource_type === 'system' ? '系统声明的资源由代码维护' : undefined
          }
          loading={statusPendingId === record.id}
          onChange={(status) => onStatusChange(record, status)}
        />
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
      title: '创建时间',
      dataIndex: 'created_at',
      width: 170,
      render: (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm:ss'),
    },
    ...recycleColumns,
    {
      title: '操作',
      width: recycleMode ? 100 : 120,
      render: (_, record) => {
        if (record.resource_type === 'system') {
          return <span style={{ color: '#999' }}>代码维护</span>
        }
        if (recycleMode) {
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
        }
        return (
          <Space size={8}>
            <Tooltip title="编辑">
              <Button
                type="text"
                icon={<IconEdit size={16} />}
                onClick={() => onEdit(record)}
              />
            </Tooltip>
            <Tooltip title="删除">
              <Button
                type="text"
                danger
                icon={<IconTrash size={16} />}
                onClick={() => onDelete(record)}
              />
            </Tooltip>
          </Space>
        )
      },
    },
  ]

  return (
    <Table<Resource>
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={resources}
      pagination={false}
      expandable={{
        expandedRowRender: (record) => (
          <PermissionTable
            resource={record}
            recycleMode={recycleMode}
            statusPendingId={permissionStatusPendingId}
            onCreate={onCreatePermission}
            onEdit={onEditPermission}
            onDelete={onDeletePermission}
            onStatusChange={onPermissionStatusChange}
          />
        ),
      }}
    />
  )
}
