import { useQueryClient } from '@tanstack/react-query'
import { App } from 'antd'
import { useMemo, useState } from 'react'

import { isApiError } from '@shared/api'
import { Platform } from '@shared/platform'

import { getRole } from './api/roleApi'
import { RoleFormDrawer } from './components/RoleFormDrawer'
import { RoleToolbar } from './components/RoleToolbar'
import { RoleTable } from './components/desktop/RoleTable'
import { RoleCardList } from './components/mobile/RoleCardList'
import { useRoleMutations } from './hooks/useRoleMutations'
import { useRoles } from './hooks/useRoles'
import type { Role, RoleDetail, RoleFormValues } from './types'

interface DialogState {
  open: boolean
  mode: 'create' | 'edit'
  detail?: RoleDetail
}

/**
 * 角色管理页：列表 + 新建/编辑（基础信息 + 数据范围部门 + 权限树，一次提交）。
 * 写接口为「全合」：POST / PUT 都提交整份角色（PUT 语义：传什么就设成什么）。
 * 编辑需先拉 `GET /roles/{id}` 详情拿权限/部门集再填表。
 */
export default function RolePage() {
  const { data: roles = [], isLoading, error } = useRoles()
  const { create, update, remove } = useRoleMutations()
  const queryClient = useQueryClient()
  const { message, modal } = App.useApp()
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
  const openEdit = async (role: Role) => {
    try {
      const detail = await queryClient.fetchQuery({
        queryKey: ['role', role.id],
        queryFn: () => getRole(role.id),
      })
      setDialog({ open: true, mode: 'edit', detail })
    } catch (err) {
      message.error(isApiError(err) ? err.message : '加载角色详情失败')
    }
  }
  const close = () => setDialog((prev) => ({ ...prev, open: false }))

  const submit = (values: RoleFormValues, permissionIds: string[]) => {
    const dataScope = values.data_scope
    // 部门集仅在 custom 语义下有效；其余范围传空（整体替换 = 传什么就是什么）
    const deptIds = dataScope === 'custom' ? (values.dept_ids ?? []) : []
    const description = values.description?.trim() || null

    if (dialog.mode === 'edit' && dialog.detail) {
      update.mutate(
        {
          id: dialog.detail.id,
          body: {
            name: values.name.trim(),
            data_scope: dataScope,
            description,
            status: values.status ?? dialog.detail.status,
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

  const pending = create.isPending || update.isPending

  return (
    <div>
      <RoleToolbar keyword={keyword} onKeywordChange={setKeyword} onCreate={openCreate} />
      <Platform
        desktop={
          <RoleTable
            roles={filtered}
            loading={isLoading}
            error={error}
            onEdit={openEdit}
            onDelete={confirmDelete}
          />
        }
        mobile={
          <RoleCardList
            roles={filtered}
            loading={isLoading}
            error={error}
            onEdit={openEdit}
            onDelete={confirmDelete}
          />
        }
      />
      <RoleFormDrawer
        open={dialog.open}
        mode={dialog.mode}
        initial={dialog.detail}
        pending={pending}
        onSubmit={submit}
        onClose={close}
      />
    </div>
  )
}
