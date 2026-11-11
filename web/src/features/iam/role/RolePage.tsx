import { App } from 'antd'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { usePermission } from '@features/auth'
import { Platform } from '@shared/platform'

import type { SortOrder } from '../types'
import { RoleDetailDrawer } from './components/RoleDetailDrawer'
import { RoleFormDrawer } from './components/RoleFormDrawer'
import { RoleMembersDrawer } from './components/RoleMembersDrawer'
import { RoleToolbar } from './components/RoleToolbar'
import { RoleTable } from './components/desktop/RoleTable'
import { RoleCardList } from './components/mobile/RoleCardList'
import { useRoleMutations } from './hooks/useRoleMutations'
import { useRoles } from './hooks/useRoles'
import type { GetRolesQuery, Role, RoleFormValues, RoleListItem, RoleSortField } from './types'

interface DialogState {
  open: boolean
  mode: 'create' | 'edit' | 'view'
  role?: Role
}

/**
 * 角色管理页：列表 + 新建/编辑/查看（基础信息 + 数据范围部门 + 权限树）。
 * 列表已含权限/部门集（后端同 schema），故「查看/编辑」直接用行数据、无需再拉详情。
 * 写接口「全合」：POST / PUT 都提交整份角色（PUT 语义：传什么就设成什么）。
 */
export default function RolePage() {
  const [params, setParams] = useSearchParams()
  const { create, update, remove, setStatus, restore, hardDelete } = useRoleMutations()
  const { modal } = App.useApp()
  const { can } = usePermission()
  const canReadMembers = can('iam:user_role:read') && can('iam:user:read')
  const canManageMembers = can('iam:user_role:assign') && can('iam:user:read')
  const canViewMembers = canReadMembers
  const [dialog, setDialog] = useState<DialogState>({ open: false, mode: 'create' })
  const [membersTarget, setMembersTarget] = useState<RoleListItem | null>(null)

  const page = Number(params.get('page') ?? '1') || 1
  const pageSize = Number(params.get('page_size') ?? '10') || 10
  const keyword = params.get('keyword') ?? ''
  const recycleMode = params.get('deleted') === 'true'
  const sortBy = (params.get('sort_by') as RoleSortField | null) ?? 'created_at'
  const order = (params.get('order') as SortOrder | null) ?? 'desc'

  const query: GetRolesQuery = {
    page,
    page_size: pageSize,
    keyword: keyword || undefined,
    deleted: recycleMode || undefined,
    sort_by: sortBy,
    order,
  }
  const { data, isLoading, error } = useRoles(query)
  const roles = data?.data ?? []

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
  const openView = (role: Role) => setDialog({ open: true, mode: 'view', role })
  const openEdit = (role: Role) => setDialog({ open: true, mode: 'edit', role })
  const close = () => setDialog((prev) => ({ ...prev, open: false }))

  const submit = (values: RoleFormValues, permissionIds: string[]) => {
    const dataScope = values.data_scope
    // 部门集仅在 custom 语义下有效；其余范围传空（整体替换 = 传什么就是什么）
    const deptIds = dataScope === 'custom' ? (values.dept_ids ?? []) : []
    const description = values.description?.trim() || null

    if (dialog.mode === 'edit' && dialog.role) {
      update.mutate(
        {
          id: dialog.role.id,
          body: {
            name: values.name.trim(),
            data_scope: dataScope,
            description,
            status: values.status ?? dialog.role.status,
            permission_ids: permissionIds,
            dept_ids: deptIds,
          },
        },
        { onSuccess: close },
      )
    } else {
      create.mutate(
        {
          code: values.code.trim(),
          name: values.name.trim(),
          data_scope: dataScope,
          description,
          status: values.status ?? 'active',
          permission_ids: permissionIds,
          dept_ids: deptIds,
        },
        { onSuccess: close },
      )
    }
  }

  const confirmDelete = (role: Role) =>
    modal.confirm({
      title: `删除角色「${role.name}」？`,
      okButtonProps: { danger: true },
      onOk: () => remove.mutateAsync(role.id),
    })

  const confirmRestore = (role: Role) =>
    modal.confirm({
      title: `恢复角色「${role.name}」？`,
      content: '恢复后保留删除前的状态。',
      onOk: () => restore.mutateAsync(role.id),
    })

  const confirmHardDelete = (role: Role) =>
    modal.confirm({
      title: `彻底删除角色「${role.name}」？`,
      content: '此操作不可恢复。',
      okButtonProps: { danger: true },
      onOk: () => hardDelete.mutateAsync(role.id),
    })

  const pending = create.isPending || update.isPending

  return (
    <div>
      <RoleToolbar
        keyword={keyword}
        recycleMode={recycleMode}
        onKeywordChange={(value) => updateQuery({ keyword: value.trim() || undefined })}
        onRecycleModeChange={(next) => updateQuery({ deleted: next ? 'true' : undefined })}
        onCreate={openCreate}
      />
      <Platform
        desktop={
          <RoleTable
            roles={roles}
            loading={isLoading}
            error={error}
            total={data?.total ?? 0}
            page={page}
            pageSize={pageSize}
            recycleMode={recycleMode}
            canViewMembers={!recycleMode && canViewMembers}
            onViewMembers={setMembersTarget}
            onView={openView}
            onEdit={openEdit}
            onDelete={confirmDelete}
            onRestore={confirmRestore}
            onHardDelete={confirmHardDelete}
            statusPendingId={setStatus.isPending ? setStatus.variables?.id : undefined}
            onStatusChange={(role, status) => setStatus.mutate({ id: role.id, status })}
            sortBy={sortBy}
            order={order}
            onSortChange={(nextSortBy, nextOrder) =>
              updateQuery({
                sort_by: nextSortBy ?? undefined,
                order: nextOrder ?? undefined,
              })
            }
            onPageChange={(nextPage, nextSize) =>
              updateQuery({ page: String(nextPage), page_size: String(nextSize) })
            }
          />
        }
        mobile={
          <RoleCardList
            roles={roles}
            loading={isLoading}
            error={error}
            recycleMode={recycleMode}
            canViewMembers={!recycleMode && canViewMembers}
            onViewMembers={setMembersTarget}
            onView={openView}
            onEdit={openEdit}
            onDelete={confirmDelete}
            onRestore={confirmRestore}
            onHardDelete={confirmHardDelete}
          />
        }
      />
      {dialog.mode === 'view' ? (
        <RoleDetailDrawer open={dialog.open} roleId={dialog.role?.id} onClose={close} />
      ) : (
        <RoleFormDrawer
          open={dialog.open}
          mode={dialog.mode}
          initial={dialog.role}
          pending={pending}
          onSubmit={submit}
          onClose={close}
        />
      )}
      {membersTarget && (
        <RoleMembersDrawer
          role={membersTarget}
          canManage={canManageMembers}
          onClose={() => setMembersTarget(null)}
        />
      )}
    </div>
  )
}
