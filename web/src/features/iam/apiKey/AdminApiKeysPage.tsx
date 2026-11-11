import { App, Select, Space } from 'antd'
import { useSearchParams } from 'react-router-dom'

import { usePermission } from '@features/auth'
import { Platform } from '@shared/platform'

import { RecycleModeSwitch } from '../components/RecycleModeSwitch'
import { UserSelect } from '../components/UserSelect'
import { STATUS_OPTIONS } from '../constants'
import type { Status } from '../types'
import { ApiKeyTable } from './components/desktop/ApiKeyTable'
import { ApiKeyCardList } from './components/mobile/ApiKeyCardList'
import { useApiKeyMutations } from './hooks/useApiKeyMutations'
import { useAdminApiKeys } from './hooks/useApiKeys'
import type { ApiKeyRow } from './types'

/** 后台 · API 密钥管理：按数据范围列出所有 key，支持用户/状态/回收站过滤、启停与吊销。 */
export default function AdminApiKeysPage() {
  const [params, setParams] = useSearchParams()
  const { modal } = App.useApp()
  const { can } = usePermission()
  const { setStatus, revoke } = useApiKeyMutations()

  const userId = params.get('user_id') ?? undefined
  const status = (params.get('status') as Status | null) ?? undefined
  const recycleMode = params.get('deleted') === 'true'

  const { data = [], isLoading, error } = useAdminApiKeys({
    user_id: userId,
    status,
    deleted: recycleMode || undefined,
  })

  const canReadUsers = can('iam:user:read')
  const canUpdate = !recycleMode && can('iam:api_key:update')
  const canDelete = !recycleMode && can('iam:api_key:delete')
  const statusPendingId = setStatus.isPending ? setStatus.variables?.id : undefined

  const updateQuery = (patch: Record<string, string | undefined>) => {
    const next = new URLSearchParams(params)
    for (const [key, value] of Object.entries(patch)) {
      if (value) next.set(key, value)
      else next.delete(key)
    }
    setParams(next, { replace: true })
  }

  const confirmRevoke = (key: ApiKeyRow) =>
    modal.confirm({
      title: `吊销 API Key「${key.name}」？`,
      content: `所属用户：${key.username || '未知用户'}。吊销后无法恢复。`,
      okText: '吊销',
      okButtonProps: { danger: true },
      onOk: () => revoke.mutateAsync({ id: key.id, admin: true }),
    })

  const tableProps = {
    keys: data,
    loading: isLoading,
    error,
    admin: true,
    recycleMode,
    canUpdate,
    canDelete,
    statusPendingId,
    onToggle: (key: ApiKeyRow, next: Status) =>
      setStatus.mutate({ id: key.id, status: next, admin: true }),
    onRevoke: confirmRevoke,
  }

  return (
    <div>
      <Space style={{ display: 'flex', marginBottom: 16, flexWrap: 'wrap' }} size={12}>
        <RecycleModeSwitch
          value={recycleMode}
          onChange={(next) => updateQuery({ deleted: next ? 'true' : undefined })}
        />
        {canReadUsers && (
          <div style={{ width: 240 }}>
            <UserSelect
              value={userId}
              onChange={(value) => updateQuery({ user_id: value })}
              placeholder="筛选所属用户"
            />
          </div>
        )}
        <Select
          allowClear
          placeholder="状态"
          style={{ width: 110 }}
          value={status}
          options={STATUS_OPTIONS}
          onChange={(value) => updateQuery({ status: value })}
        />
      </Space>

      <Platform
        desktop={<ApiKeyTable {...tableProps} />}
        mobile={<ApiKeyCardList {...tableProps} />}
      />
    </div>
  )
}
