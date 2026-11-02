import { App } from 'antd'
import { useMemo, useState } from 'react'

import { Platform } from '@shared/platform'

import { PermissionFormDialog } from './components/PermissionFormDialog'
import { ResourceFormDrawer } from './components/ResourceFormDrawer'
import { ResourceToolbar } from './components/ResourceToolbar'
import { DeletedPermissionTable } from './components/desktop/DeletedPermissionTable'
import { ResourceTable } from './components/desktop/ResourceTable'
import { DeletedPermissionCardList } from './components/mobile/DeletedPermissionCardList'
import { ResourceCardList } from './components/mobile/ResourceCardList'
import { usePermissions } from './hooks/usePermissions'
import { useResourceMutations } from './hooks/useResourceMutations'
import { useResources } from './hooks/useResources'
import type {
  PermissionFormValues,
  PermissionListItem,
  RecycleKind,
  Resource,
  ResourceFormValues,
  ResourcePermission,
} from './types'

interface ResourceDialogState {
  open: boolean
  mode: 'create' | 'edit'
  resource?: Resource
}

interface PermissionDialogState {
  open: boolean
  mode: 'create' | 'edit'
  resource?: Resource
  permission?: ResourcePermission
}

/**
 * 资源管理页：资源列表 + 行内展开权限。
 * - SYSTEM 条目由代码声明拥有，后台只读（但可在其下新增 CUSTOM 权限）。
 * - CUSTOM 资源/权限可增删改；资源回收站支持恢复与彻底删除。
 * - 权限回收站只列「资源仍存活」的已删权限（随资源删的跟着资源走）。
 */
export default function ResourcePage() {
  const [recycleMode, setRecycleMode] = useState(false)
  const [recycleKind, setRecycleKind] = useState<RecycleKind>('resources')
  const [keyword, setKeyword] = useState('')
  const [dialog, setDialog] = useState<ResourceDialogState>({ open: false, mode: 'create' })
  const [permissionDialog, setPermissionDialog] = useState<PermissionDialogState>({
    open: false,
    mode: 'create',
  })

  // 回收站内资源展开后要能只读看到其全部权限（含随资源删的）
  const { data: resources = [], isLoading, error } = useResources(recycleMode, recycleMode)
  const permissionsQuery = usePermissions(
    true,
    recycleMode && recycleKind === 'permissions',
  )
  const mutations = useResourceMutations()
  const { modal } = App.useApp()

  const filteredResources = useMemo(() => {
    const query = keyword.trim().toLowerCase()
    if (!query) return resources
    return resources.filter(
      (resource) =>
        resource.module.toLowerCase().includes(query) ||
        resource.code.toLowerCase().includes(query) ||
        resource.name.toLowerCase().includes(query),
    )
  }, [resources, keyword])

  const filteredPermissions = useMemo(() => {
    const query = keyword.trim().toLowerCase()
    const permissions = permissionsQuery.data ?? []
    if (!query) return permissions
    return permissions.filter(
      (permission) =>
        permission.resource_key.toLowerCase().includes(query) ||
        permission.resource_name.toLowerCase().includes(query) ||
        permission.action.toLowerCase().includes(query) ||
        permission.name.toLowerCase().includes(query) ||
        permission.key.toLowerCase().includes(query),
    )
  }, [permissionsQuery.data, keyword])

  const handleRecycleModeChange = (value: boolean) => {
    setRecycleMode(value)
    if (value) setRecycleKind('resources')
  }

  const openCreate = () => setDialog({ open: true, mode: 'create' })
  const openEdit = (resource: Resource) => setDialog({ open: true, mode: 'edit', resource })
  const closeResourceDialog = () => setDialog((prev) => ({ ...prev, open: false }))
  const closePermissionDialog = () =>
    setPermissionDialog((prev) => ({ ...prev, open: false }))

  const submitResource = (values: ResourceFormValues) => {
    const description = values.description?.trim() || null
    if (dialog.mode === 'edit' && dialog.resource) {
      mutations.update.mutate(
        {
          id: dialog.resource.id,
          body: { name: values.name.trim(), description },
        },
        { onSuccess: closeResourceDialog },
      )
    } else {
      mutations.create.mutate(
        {
          module: values.module.trim(),
          code: values.code.trim(),
          name: values.name.trim(),
          description,
        },
        { onSuccess: closeResourceDialog },
      )
    }
  }

  const submitPermission = (values: PermissionFormValues) => {
    const description = values.description?.trim() || null
    if (permissionDialog.mode === 'edit' && permissionDialog.permission) {
      mutations.updatePerm.mutate(
        {
          id: permissionDialog.permission.id,
          body: { name: values.name.trim(), description },
        },
        { onSuccess: closePermissionDialog },
      )
      return
    }
    if (permissionDialog.resource) {
      mutations.createPerm.mutate(
        {
          resource_id: permissionDialog.resource.id,
          action: values.action.trim(),
          name: values.name.trim(),
          description,
        },
        { onSuccess: closePermissionDialog },
      )
    }
  }

  const confirmDelete = (resource: Resource) =>
    modal.confirm({
      title: `删除资源「${resource.name}」？`,
      content: '其下仍存活的权限会一并软删，可在回收站恢复。',
      okButtonProps: { danger: true },
      onOk: () => mutations.remove.mutateAsync(resource.id),
    })

  const confirmRestore = (resource: Resource) =>
    modal.confirm({
      title: `恢复资源「${resource.name}」？`,
      content: '只恢复随资源一起被删的权限；此前单独删除的权限仍留在权限回收站。',
      onOk: () => mutations.restore.mutateAsync(resource.id),
    })

  const confirmHardDelete = (resource: Resource) => {
    const isSystem = resource.resource_type === 'system'
    return modal.confirm({
      title: isSystem
        ? `清理系统残留「${resource.name}」？`
        : `彻底删除资源「${resource.name}」？`,
      content: isSystem
        ? '代码声明已移除；彻底删除后若重新声明会创建新 id，角色原有授权不会自动恢复。'
        : '会连其下所有权限（含此前单独删除的）一起物理删除，并清理角色引用。',
      okButtonProps: { danger: true },
      onOk: () => mutations.hardDelete.mutateAsync(resource.id),
    })
  }

  const openCreatePermission = (resource: Resource) =>
    setPermissionDialog({ open: true, mode: 'create', resource })

  const openEditPermission = (resource: Resource, permission: ResourcePermission) =>
    setPermissionDialog({ open: true, mode: 'edit', resource, permission })

  const confirmDeletePermission = (_resource: Resource, permission: ResourcePermission) =>
    modal.confirm({
      title: `删除权限「${permission.name}」？`,
      content: '删除后会进入「回收站 · 权限」，可单独恢复。',
      okButtonProps: { danger: true },
      onOk: () => mutations.removePerm.mutateAsync(permission.id),
    })

  const confirmRestoreDeletedPermission = (permission: PermissionListItem) =>
    modal.confirm({
      title: `恢复权限「${permission.name}」？`,
      content: '恢复后角色中已有的该权限引用会重新生效。',
      onOk: () => mutations.restorePerm.mutateAsync(permission.id),
    })

  const confirmHardDeleteDeletedPermission = (permission: PermissionListItem) => {
    const isSystem = permission.permission_type === 'system'
    return modal.confirm({
      title: isSystem
        ? `清理系统残留「${permission.name}」？`
        : `彻底删除权限「${permission.name}」？`,
      content: isSystem
        ? '代码声明已移除；彻底删除后若重新声明会创建新 id，角色原有授权不会自动恢复。'
        : '会同时清理角色中的引用，此操作不可恢复。',
      okButtonProps: { danger: true },
      onOk: () => mutations.hardDeletePerm.mutateAsync(permission.id),
    })
  }

  const changeResourceStatus = (resource: Resource, status: 'active' | 'disabled') =>
    mutations.setStatus.mutate({ id: resource.id, status })

  const changePermissionStatus = (
    _resource: Resource,
    permission: ResourcePermission,
    status: 'active' | 'disabled',
  ) => mutations.setPermStatus.mutate({ id: permission.id, status })

  const sharedViewProps = {
    resources: filteredResources,
    loading: isLoading,
    error,
    recycleMode,
    statusPendingId: mutations.setStatus.isPending ? mutations.setStatus.variables?.id : undefined,
    permissionStatusPendingId: mutations.setPermStatus.isPending
      ? mutations.setPermStatus.variables?.id
      : undefined,
    onEdit: openEdit,
    onDelete: confirmDelete,
    onRestore: confirmRestore,
    onHardDelete: confirmHardDelete,
    onStatusChange: changeResourceStatus,
    onCreatePermission: openCreatePermission,
    onEditPermission: openEditPermission,
    onDeletePermission: confirmDeletePermission,
    onPermissionStatusChange: changePermissionStatus,
  }

  const deletedPermissionViewProps = {
    permissions: filteredPermissions,
    loading: permissionsQuery.isLoading,
    error: permissionsQuery.error,
    onRestore: confirmRestoreDeletedPermission,
    onHardDelete: confirmHardDeleteDeletedPermission,
  }

  const pending = mutations.create.isPending || mutations.update.isPending
  const permissionPending = mutations.createPerm.isPending || mutations.updatePerm.isPending
  const showPermissionRecycle = recycleMode && recycleKind === 'permissions'

  return (
    <div>
      <ResourceToolbar
        keyword={keyword}
        recycleMode={recycleMode}
        recycleKind={recycleKind}
        onKeywordChange={setKeyword}
        onRecycleModeChange={handleRecycleModeChange}
        onRecycleKindChange={setRecycleKind}
        onCreate={openCreate}
      />
      {showPermissionRecycle ? (
        <Platform
          desktop={<DeletedPermissionTable {...deletedPermissionViewProps} />}
          mobile={<DeletedPermissionCardList {...deletedPermissionViewProps} />}
        />
      ) : (
        <Platform
          desktop={<ResourceTable {...sharedViewProps} />}
          mobile={<ResourceCardList {...sharedViewProps} />}
        />
      )}
      <ResourceFormDrawer
        open={dialog.open}
        mode={dialog.mode}
        initial={dialog.resource}
        pending={pending}
        onSubmit={submitResource}
        onClose={closeResourceDialog}
      />
      <PermissionFormDialog
        open={permissionDialog.open}
        mode={permissionDialog.mode}
        initial={permissionDialog.permission}
        pending={permissionPending}
        onSubmit={submitPermission}
        onClose={closePermissionDialog}
      />
    </div>
  )
}
