import { App } from 'antd'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { usePermission } from '@features/auth'
import { Platform } from '@shared/platform'

import { UserDetailDrawer } from './components/UserDetailDrawer'
import { UserFormDrawer } from './components/UserFormDrawer'
import { UserToolbar } from './components/UserToolbar'
import { UserTable } from './components/desktop/UserTable'
import { UserCardList } from './components/mobile/UserCardList'
import { useUserMutations } from './hooks/useUserMutations'
import { useUsers } from './hooks/useUsers'
import type { GetUsersQuery, UserFormValues, UserListItem, UserStatus, UserType } from './types'

interface DialogState {
  open: boolean
  mode: 'create' | 'edit'
  userId?: string
}

/**
 * 【平台模式范例 · 分叉档】
 *
 * 页面**只写一份**：
 *  1. 取数（useUsers）两端共用 —— 业务逻辑不感知设备；
 *  2. 工具栏（UserToolbar）两端共用；
 *  3. 只有「列表渲染」确实不同（桌面表格 / 移动卡片），才用 <Platform> 分叉。
 *
 * 筛选/分页状态放 **URL query**（可分享、刷新不丢）；改动即触发 TanStack Query 重新取数。
 */
export default function UserPage() {
  const [params, setParams] = useSearchParams()
  const [viewingId, setViewingId] = useState<string>()
  const [dialog, setDialog] = useState<DialogState>({ open: false, mode: 'create' })
  const { modal } = App.useApp()
  const { me } = usePermission()
  const { create, update, remove, setStatus, restore, hardDelete } = useUserMutations()

  const page = Number(params.get('page') ?? '1') || 1
  const pageSize = Number(params.get('page_size') ?? '10') || 10
  const keyword = params.get('keyword') ?? ''
  const status = (params.get('status') as UserStatus | null) ?? undefined
  const userType = (params.get('user_type') as UserType | null) ?? undefined
  const recycleMode = params.get('deleted') === 'true'

  const query: GetUsersQuery = {
    page,
    page_size: pageSize,
    keyword: keyword || undefined,
    status,
    user_type: userType,
    deleted: recycleMode || undefined,
  }
  const { data, isLoading, error } = useUsers(query)
  const users = data?.data ?? []

  /** 改筛选/分页：patch 的键即 URL query 参数名；不带 page 的改动回到第 1 页。 */
  const updateQuery = (patch: Record<string, string | undefined>) => {
    const next = new URLSearchParams(params)
    for (const [key, value] of Object.entries(patch)) {
      if (value) next.set(key, value)
      else next.delete(key)
    }
    if (!('page' in patch)) next.set('page', '1')
    setParams(next, { replace: true })
  }

  const openCreate = () => setDialog({ open: true, mode: 'create' })
  const openEdit = (user: UserListItem) =>
    setDialog({ open: true, mode: 'edit', userId: user.id })
  const close = () => setDialog((prev) => ({ ...prev, open: false }))

  const submit = (values: UserFormValues) => {
    const email = values.email?.trim() || null
    const phone = values.phone?.trim() || null
    const description = values.description?.trim() || null
    const deptId = values.dept_id ?? null
    const roleIds = values.role_ids ?? []

    if (dialog.mode === 'edit' && dialog.userId) {
      update.mutate(
        {
          id: dialog.userId,
          body: {
            nickname: values.nickname!.trim(),
            email,
            phone,
            status: values.status,
            description,
            role_ids: roleIds,
            dept_id: deptId,
          },
        },
        { onSuccess: close },
      )
    } else {
      create.mutate(
        {
          username: values.username!.trim(),
          nickname: values.nickname?.trim() || undefined,
          password: values.password!,
          email,
          phone,
          status: values.status,
          description,
          role_ids: roleIds,
          dept_id: deptId,
        },
        { onSuccess: close },
      )
    }
  }

  const confirmDelete = (user: UserListItem) =>
    modal.confirm({
      title: `删除用户「${user.username}」？`,
      content: '删除后可在回收站恢复。',
      okButtonProps: { danger: true },
      onOk: () => remove.mutateAsync(user.id),
    })

  const confirmRestore = (user: UserListItem) =>
    modal.confirm({
      title: `恢复用户「${user.username}」？`,
      content: '恢复后保留删除前的状态。',
      onOk: () => restore.mutateAsync(user.id),
    })

  const confirmHardDelete = (user: UserListItem) =>
    modal.confirm({
      title: `彻底删除用户「${user.username}」？`,
      content: '此操作不可恢复。',
      okButtonProps: { danger: true },
      onOk: () => hardDelete.mutateAsync(user.id),
    })

  const pending = create.isPending || update.isPending

  return (
    <div>
      <UserToolbar
        keyword={keyword}
        status={status}
        userType={userType}
        recycleMode={recycleMode}
        onChange={updateQuery}
        onRecycleModeChange={(next) => updateQuery({ deleted: next ? 'true' : undefined })}
        onCreate={openCreate}
      />
      <Platform
        desktop={
          <UserTable
            users={users}
            loading={isLoading}
            error={error}
            total={data?.total ?? 0}
            page={page}
            pageSize={pageSize}
            recycleMode={recycleMode}
            selfId={me?.user_id}
            onView={(user) => setViewingId(user.id)}
            onEdit={openEdit}
            onDelete={confirmDelete}
            onRestore={confirmRestore}
            onHardDelete={confirmHardDelete}
            statusPendingId={setStatus.isPending ? setStatus.variables?.id : undefined}
            onStatusChange={(user, status) => setStatus.mutate({ id: user.id, status })}
            onPageChange={(nextPage, nextSize) =>
              updateQuery({ page: String(nextPage), page_size: String(nextSize) })
            }
          />
        }
        mobile={
          <UserCardList
            users={users}
            loading={isLoading}
            error={error}
            recycleMode={recycleMode}
            onView={(user) => setViewingId(user.id)}
            onEdit={openEdit}
            onDelete={confirmDelete}
            onRestore={confirmRestore}
            onHardDelete={confirmHardDelete}
          />
        }
      />
      <UserDetailDrawer
        open={!!viewingId}
        userId={viewingId}
        onClose={() => setViewingId(undefined)}
      />
      <UserFormDrawer
        open={dialog.open}
        mode={dialog.mode}
        userId={dialog.userId}
        pending={pending}
        onSubmit={submit}
        onClose={close}
      />
    </div>
  )
}
