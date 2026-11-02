import { App } from 'antd'
import { useMemo, useState } from 'react'

import { Platform } from '@shared/platform'

import { RoleDetailDrawer } from './components/RoleDetailDrawer'
import { RoleFormDrawer } from './components/RoleFormDrawer'
import { RoleToolbar } from './components/RoleToolbar'
import { RoleTable } from './components/desktop/RoleTable'
import { RoleCardList } from './components/mobile/RoleCardList'
import { useRoleMutations } from './hooks/useRoleMutations'
import { useRoles } from './hooks/useRoles'
import type { Role, RoleFormValues } from './types'

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
  const [recycleMode, setRecycleMode] = useState(false)
  const { data: roles = [], isLoading, error } = useRoles(recycleMode)
  const { create, update, remove, setStatus, restore, hardDelete } = useRoleMutations()
  const { modal } = App.useApp()
  const [keyword, setKeyword] = useState('')
  const [dialog, setDialog] = useState<DialogState>({ open: false, mode: 'create' })

  const filtered = useMemo(() => {
    const query = keyword.trim().toLowerCase()
    if (!query) return roles
    return roles.filter(
      (role) => role.name.toLowerCase().includes(query) || role.code.toLowerCase().includes(query),
    )
  }, [roles, keyword])

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
        onKeywordChange={setKeyword}
        onRecycleModeChange={setRecycleMode}
        onCreate={openCreate}
      />
      <Platform
        desktop={
          <RoleTable
            roles={filtered}
            loading={isLoading}
            error={error}
            recycleMode={recycleMode}
            onView={openView}
            onEdit={openEdit}
            onDelete={confirmDelete}
            onRestore={confirmRestore}
            onHardDelete={confirmHardDelete}
            statusPendingId={setStatus.isPending ? setStatus.variables?.id : undefined}
            onStatusChange={(role, status) => setStatus.mutate({ id: role.id, status })}
          />
        }
        mobile={
          <RoleCardList
            roles={filtered}
            loading={isLoading}
            error={error}
            recycleMode={recycleMode}
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
    </div>
  )
}
