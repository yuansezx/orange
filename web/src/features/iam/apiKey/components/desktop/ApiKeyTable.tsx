import { Alert, Button, Space, Table, Tag, Tooltip } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'

import { StatusSwitch } from '../../../components/StatusSwitch'
import { STATUS_COLORS, STATUS_LABELS } from '../../../constants'
import type { Status } from '../../../types'
import { API_KEY_DATA_SCOPE_LABELS } from '../../constants'
import type { ApiKeyRow } from '../../types'
import { formatTime, isExpired } from '../../utils'

interface Props {
  keys: ApiKeyRow[]
  loading: boolean
  error: Error | null
  /** 管理端：多一列所属用户。 */
  admin?: boolean
  recycleMode?: boolean
  canUpdate: boolean
  canDelete: boolean
  statusPendingId?: string
  onEdit?: (key: ApiKeyRow) => void
  onToggle: (key: ApiKeyRow, status: Status) => void
  onRevoke: (key: ApiKeyRow) => void
}

function dataScopeText(key: ApiKeyRow) {
  if (key.data_scope_kind === 'custom') {
    return `${API_KEY_DATA_SCOPE_LABELS.custom}（${key.data_scope_dept_ids.length}）`
  }
  return API_KEY_DATA_SCOPE_LABELS[key.data_scope_kind]
}

/** 【分叉档 · 桌面】API Key 表格；自助/管理共用，管理端多「所属用户」列。 */
export function ApiKeyTable({
  keys,
  loading,
  error,
  admin = false,
  recycleMode = false,
  canUpdate,
  canDelete,
  statusPendingId,
  onEdit,
  onToggle,
  onRevoke,
}: Props) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const columns: TableProps<ApiKeyRow>['columns'] = [
    ...(admin
      ? [
          {
            title: '所属用户',
            dataIndex: 'username',
            width: 140,
            render: (value: string | null | undefined) => value || '—',
          },
        ]
      : []),
    { title: '名称', dataIndex: 'name', width: 180, ellipsis: true },
    {
      title: '令牌',
      dataIndex: 'token_masked',
      width: 190,
      render: (value: string) => <span style={{ fontFamily: 'monospace' }}>{value}</span>,
    },
    {
      title: '权限',
      key: 'scopes',
      width: 90,
      render: (_, key) => (
        <Tooltip
          title={<div style={{ whiteSpace: 'pre-line' }}>{key.scopes.join('\n')}</div>}
        >
          <span>{key.scopes.length} 项</span>
        </Tooltip>
      ),
    },
    {
      title: '数据范围',
      key: 'dataScope',
      width: 160,
      render: (_, key) => dataScopeText(key),
    },
    {
      title: '状态',
      key: 'status',
      width: 110,
      render: (_, key) => {
        if (recycleMode) return <Tag>已吊销</Tag>
        if (!canUpdate) {
          return <Tag color={STATUS_COLORS[key.status]}>{STATUS_LABELS[key.status]}</Tag>
        }
        return (
          <StatusSwitch
            status={key.status}
            loading={statusPendingId === key.id}
            onChange={(status) => onToggle(key, status)}
          />
        )
      },
    },
    {
      title: '过期时间',
      key: 'expiresAt',
      width: 190,
      render: (_, key) => {
        if (!key.expires_at) return '永久'
        return (
          <span>
            {dayjs(key.expires_at).format('YYYY-MM-DD HH:mm')}
            {isExpired(key) && (
              <Tag color="error" style={{ marginInlineStart: 6 }}>
                已过期
              </Tag>
            )}
          </span>
        )
      },
    },
    {
      title: '最近使用',
      dataIndex: 'last_used_at',
      width: 160,
      render: (value: string | null) => formatTime(value),
    },
    {
      title: '操作',
      key: 'actions',
      width: 130,
      render: (_, key) => {
        if (recycleMode) return '—'
        const actions = (
          <Space size={4}>
            {onEdit && (
              <Button type="link" size="small" onClick={() => onEdit(key)}>
                编辑
              </Button>
            )}
            {canDelete && (
              <Button type="link" size="small" danger onClick={() => onRevoke(key)}>
                吊销
              </Button>
            )}
          </Space>
        )
        return onEdit || canDelete ? actions : '—'
      },
    },
  ]

  return (
    <Table<ApiKeyRow>
      rowKey="id"
      size="small"
      loading={loading}
      columns={columns}
      dataSource={keys}
      pagination={false}
      scroll={{ x: 1150 }}
    />
  )
}
