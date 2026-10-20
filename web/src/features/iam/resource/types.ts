import type { AuditFields, Status } from '../types'

/** 来源：SYSTEM = 代码声明（后台只读）；CUSTOM = 后台自建。 */
export type SourceType = 'system' | 'custom'

/** 回收站内的对象类型：资源 / 单独删除的权限。 */
export type RecycleKind = 'resources' | 'permissions'

/** 权限读模型——对齐后端 `PermissionOut`（数据 + 审计）。 */
export interface ResourcePermission extends AuditFields {
  id: string
  resource_id: string
  action: string
  key: string
  name: string
  description: string | null
  status: Status
  permission_type: SourceType
}

/** 资源读模型——对齐后端 `ResourceOut`（数据 + 审计 + 权限集）。 */
export interface Resource extends AuditFields {
  id: string
  module: string
  code: string
  key: string
  name: string
  description: string | null
  status: Status
  resource_type: SourceType
  permissions: ResourcePermission[]
}

/** 扁平权限列表项——对齐后端 `PermissionListItemOut`（含所属资源上下文）。 */
export interface PermissionListItem extends ResourcePermission {
  resource_key: string
  resource_name: string
}

/** 资源列表查询参数。 */
export interface GetResourcesQuery {
  deleted?: boolean
  include_deleted_permissions?: boolean
}

/** 新建自定义资源。 */
export interface CreateResourceReq {
  module: string
  code: string
  name: string
  description?: string | null
}

/** 更新资源（module/code 是身份，不可改）。 */
export interface UpdateResourceReq {
  name: string
  description?: string | null
}

/** 资源表单值。 */
export interface ResourceFormValues {
  module: string
  code: string
  name: string
  description?: string
}

/** 新建自定义权限。 */
export interface CreatePermissionReq {
  resource_id: string
  action: string
  name: string
  description?: string | null
}

/** 更新权限（action 是身份，不可改）。 */
export interface UpdatePermissionReq {
  name: string
  description?: string | null
}

/** 权限表单值。 */
export interface PermissionFormValues {
  action: string
  name: string
  description?: string
}
