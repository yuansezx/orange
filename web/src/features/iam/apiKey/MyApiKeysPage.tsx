import { Alert, App, Button, Card, Empty, Tooltip } from 'antd'
import { useState } from 'react'

import { useMe } from '@features/auth'
import { Platform } from '@shared/platform'

import { ApiKeyFormDrawer } from './components/ApiKeyFormDrawer'
import { ApiKeyTokenModal } from './components/ApiKeyTokenModal'
import { ApiKeyTable } from './components/desktop/ApiKeyTable'
import { ApiKeyCardList } from './components/mobile/ApiKeyCardList'
import { useApiKeyMutations } from './hooks/useApiKeyMutations'
import { useMyApiKeys } from './hooks/useApiKeys'
import type { ApiKey, ApiKeyFormValues } from './types'
import { toCreateApiKeyReq, toUpdateApiKeyReq } from './utils'

interface DialogState {
  mode: 'create' | 'edit'
  key?: ApiKey
}

/** 个人中心 · API 密钥：自助创建/编辑/启停/吊销，明文 token 仅创建时展示一次。 */
export default function MyApiKeysPage() {
  const { data: me } = useMe()
  const { data = [], isLoading, error } = useMyApiKeys()
  const { create, update, setStatus, revoke } = useApiKeyMutations()
  const { modal } = App.useApp()

  const [dialog, setDialog] = useState<DialogState | null>(null)
  const [issued, setIssued] = useState<{ name: string; token: string } | null>(null)

  const canCreate = me != null && me.user_type !== 'super_admin'
  const pending = create.isPending || update.isPending
  const statusPendingId = setStatus.isPending ? setStatus.variables?.id : undefined

  const openCreate = () => setDialog({ mode: 'create' })
  const openEdit = (key: ApiKey) => setDialog({ mode: 'edit', key })
  const closeDialog = () => setDialog(null)

  const submit = async (values: ApiKeyFormValues) => {
    try {
      if (dialog?.mode === 'edit' && dialog.key) {
        await update.mutateAsync({ id: dialog.key.id, body: toUpdateApiKeyReq(values) })
      } else {
        const created = await create.mutateAsync(toCreateApiKeyReq(values))
        setIssued({ name: created.name, token: created.token })
      }
      closeDialog()
    } catch {
      // 错误提示由 mutation 统一处理，抽屉保留以便重试
    }
  }

  const confirmRevoke = (key: ApiKey) =>
    modal.confirm({
      title: `吊销 API Key「${key.name}」？`,
      content: '吊销后无法恢复，使用该 key 的调用会立即失效。',
      okText: '吊销',
      okButtonProps: { danger: true },
      onOk: () => revoke.mutateAsync({ id: key.id }),
    })

  const tableProps = {
    keys: data,
    loading: isLoading,
    error,
    canUpdate: true,
    canDelete: true,
    statusPendingId,
    onEdit: openEdit,
    onToggle: (key: ApiKey, status: ApiKey['status']) =>
      setStatus.mutate({ id: key.id, status }),
    onRevoke: confirmRevoke,
  }

  const title = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
      <span style={{ flex: 1, minWidth: 0 }}>API 密钥</span>
      <Tooltip title={canCreate ? undefined : '超级管理员不允许创建 API Key'}>
        <span>
          <Button type="primary" disabled={!canCreate} onClick={openCreate}>
            新建 API Key
          </Button>
        </span>
      </Tooltip>
    </div>
  )

  return (
    <Card title={title} loading={isLoading}>
      {error ? (
        <Alert type="error" message={error.message} showIcon />
      ) : data.length === 0 ? (
        <Empty description="暂无 API Key" />
      ) : (
        <Platform
          desktop={<ApiKeyTable {...tableProps} />}
          mobile={<ApiKeyCardList {...tableProps} />}
        />
      )}

      <ApiKeyFormDrawer
        open={dialog !== null}
        mode={dialog?.mode ?? 'create'}
        initial={dialog?.key}
        pending={pending}
        onSubmit={submit}
        onClose={closeDialog}
      />
      <ApiKeyTokenModal
        name={issued?.name ?? null}
        token={issued?.token ?? null}
        onClose={() => setIssued(null)}
      />
    </Card>
  )
}
