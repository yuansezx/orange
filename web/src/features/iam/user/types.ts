import type { PageQuery } from '@shared/api'

import type { AuditFields, DeptRef } from '../types'

/** 对齐后端 UserTypeEnum。 */
export type UserType = 'admin_created' | 'self_registered' | 'system' | 'super_admin'

/** 对齐后端 StatusEnum。 */
export type UserStatus = 'active' | 'disabled'

/** 用户列表读模型——字段对齐后端 `UserListItemResp`（数据 + 审计）。 */
export interface UserListItem extends AuditFields {
  id: string
  username: string
  nickname: string
  email: string | null
  phone: string | null
  user_type: UserType
  status: UserStatus
  description: string | null
  dept_id: string | null
}

/** 用户详情里的角色引用（对齐后端 `RoleRefOut`）。 */
export interface RoleRef {
  id: string
  code: string
  name: string
}

/** 用户详情——对齐后端 `UserDetailResp`（数据 + 审计 + 部门引用 + 角色）。 */
export interface UserDetail extends UserListItem {
  dept_ref: DeptRef | null
  roles: RoleRef[]
}

/** 列表查询参数——对齐后端 GetUsersReq。 */
export interface GetUsersQuery extends PageQuery {
  keyword?: string
  user_type?: UserType
  status?: UserStatus
  deleted?: boolean
  dept_id?: string
}

/** 列表视图两端的公共入参——数据在 UserPage 取好后下发，视图只负责渲染。 */
export interface UserListViewProps {
  users: UserListItem[]
  loading: boolean
  error: Error | null
  onView: (user: UserListItem) => void
}

/** 桌面表格：在视图入参上再加分页。 */
export interface UserTableProps extends UserListViewProps {
  total: number
  page: number
  pageSize: number
  onPageChange: (page: number, pageSize: number) => void
}

/** 工具栏：筛选值 + 变更回调（回调 patch 的键即 URL query 参数名）。 */
export interface UserToolbarProps {
  keyword: string
  status?: UserStatus
  userType?: UserType
  onChange: (patch: Record<string, string | undefined>) => void
  onCreate: () => void
}
