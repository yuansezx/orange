import type { AuditFields, DataScope, DeptRef, Status } from '../types'

/** 角色读模型——对齐后端 `RoleResp`（含权限集 / 数据范围部门集）。 */
export interface Role {
  id: string
  code: string
  name: string
  data_scope: DataScope
  status: Status
  description: string | null
  permission_ids: string[]
  dept_ids: string[]
}

/** 角色列表项——对齐后端 `RoleListItemResp`（数据 + 审计）。 */
export interface RoleListItem extends Role, AuditFields {}

/** 角色详情——对齐后端 `RoleDetailResp`（数据 + 审计 + 部门引用）。 */
export interface RoleDetail extends Role, AuditFields {
  dept_refs: DeptRef[]
}

/** 创建角色——对齐后端 `CreateRoleReq`（权限/部门集必填）。 */
export interface CreateRoleReq {
  code: string
  name: string
  data_scope: DataScope
  description?: string | null
  permission_ids: string[]
  dept_ids: string[]
}

/** 整体替换角色——对齐后端 `UpdateRoleReq`（PUT：传什么就设成什么）。 */
export interface UpdateRoleReq {
  name: string
  data_scope: DataScope
  description?: string | null
  status: Status
  permission_ids: string[]
  dept_ids: string[]
}

/** 角色表单值（`code` 仅新建用；`status` 编辑/查看用）。 */
export interface RoleFormValues {
  code: string
  name: string
  data_scope: DataScope
  dept_ids?: string[]
  description?: string
  status?: Status
}

// ---- 资源/权限目录（对齐后端 `CatalogResp`：模块 → 资源 → 权限） ----

export interface CatalogPermission {
  id: string
  action: string
  key: string
  name: string
  description: string | null
  status: Status
}

export interface CatalogResource {
  id: string
  module: string
  code: string
  key: string
  name: string
  description: string | null
  status: Status
  permissions: CatalogPermission[]
}

export interface CatalogModule {
  module: string
  resources: CatalogResource[]
}

export interface Catalog {
  modules: CatalogModule[]
}
