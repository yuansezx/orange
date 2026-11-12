import { ActionSheet, ErrorBlock, List, Tag } from 'antd-mobile'
import { useState } from 'react'

import { STATUS_LABELS } from '../../../constants'
import type { Status } from '../../../types'
import { API_KEY_DATA_SCOPE_LABELS } from '../../constants'
import type { ApiKey, ApiKeyRow } from '../../types'
import { formatDate, formatTime, isExpired } from '../../utils'

interface Props {
  keys: ApiKeyRow[]
  loading: boolean
  error: Error | null
  admin?: boolean
  recycleMode?: boolean
  canUpdate: boolean
  canDelete: boolean
  onEdit?: (key: ApiKeyRow) => void
  onToggle: (key: ApiKeyRow, status: Status) => void
  onRevoke: (key: ApiKeyRow) => void
}

function dataScopeText(key: ApiKey) {
  if (key.data_scope_kind === 'custom') {
    return `${API_KEY_DATA_SCOPE_LABELS.custom}（${key.data_scope_dept_ids.length}）`
  }
  return API_KEY_DATA_SCOPE_LABELS[key.data_scope_kind]
}

/** 【分叉档 · 移动】API Key 卡片列表；点项弹 ActionSheet 出操作。 */
export function ApiKeyCardList({
  keys,
  loading,
  error,
  admin = false,
  recycleMode = false,
  canUpdate,
  canDelete,
  onEdit,
  onToggle,
  onRevoke,
}: Props) {
  const [active, setActive] = useState<ApiKeyRow | null>(null)

  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <>
      <List>
        {keys.map((key) => (
          <List.Item
            key={key.id}
            onClick={() => (recycleMode ? undefined : setActive(key))}
            description={
              <div>
                <div style={{ fontFamily: 'monospace' }}>{key.token_masked}</div>
                <div>
                  {admin && key.username ? `${key.username} · ` : ''}
                  {dataScopeText(key)}
                </div>
                <div>
                  过期 {key.expires_at ? formatTime(key.expires_at) : '永久'}
                  {isExpired(key) ? '（已过期）' : ''} · 最近使用 {formatDate(key.last_used_at)}
                </div>
              </div>
            }
            extra={
              recycleMode ? (
                <Tag color="danger">已吊销</Tag>
              ) : (
                <Tag color={key.status === 'active' ? 'success' : 'default'}>
                  {STATUS_LABELS[key.status]}
                </Tag>
              )
            }
          >
            {key.name}
          </List.Item>
        ))}
        {loading && <List.Item>加载中…</List.Item>}
        {!loading && keys.length === 0 && <List.Item>暂无 API Key</List.Item>}
      </List>

      <ActionSheet
        visible={active !== null}
        cancelText="取消"
        onClose={() => setActive(null)}
        actions={[
          ...(onEdit ? [{ key: 'edit', text: '编辑' }] : []),
          {
            key: 'toggle',
            text: active?.status === 'active' ? '停用' : '启用',
            disabled: !canUpdate,
            description: canUpdate ? undefined : '无启停权限',
          },
          {
            key: 'revoke',
            text: '吊销',
            danger: true,
            disabled: !canDelete,
            description: canDelete ? '吊销后无法恢复' : '无吊销权限',
          },
        ]}
        onAction={(action) => {
          if (!active) return
          const target = active
          setActive(null)
          if (action.key === 'edit') onEdit?.(target)
          else if (action.key === 'toggle') {
            onToggle(target, target.status === 'active' ? 'disabled' : 'active')
          } else if (action.key === 'revoke') onRevoke(target)
        }}
      />
    </>
  )
}
