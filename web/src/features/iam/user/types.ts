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
  need_change_password?: boolean
}

/** 列表视图两端的公共入参——数据在 UserPage 取好后下发，视图只负责渲染。 */
export interface UserListViewProps {
  users: UserListItem[]
  loading: boolean
  error: Error | null
  /** 回收站模式：行操作换成恢复 / 彻底删除。 */
  recycleMode?: boolean
  /** 是否可重置密码（复用 `iam:user:update`）。 */
  canResetPassword: boolean
  /** 当前登录用户 id（自己的行不提供重置密码）。 */
  selfId?: string
  onResetPassword: (user: UserListItem) => void
  onView: (user: UserListItem) => void
  onEdit: (user: UserListItem) => void
  onDelete: (user: UserListItem) => void
  onRestore: (user: UserListItem) => void
  onHardDelete: (user: UserListItem) => void
}

/** 创建用户——对齐后端 `CreateUserReq`。 */
export interface CreateUserReq {
  username: string
  nickname?: string
  /** 不填则服务端生成临时密码。 */
  password?: string
  email?: string | null
  phone?: string | null
  status: UserStatus
  description?: string | null
  role_ids?: string[]
  dept_id?: string | null
}

/** 创建用户 / 重置密码的结果：服务端生成密码时回传一次明文。 */
export interface PasswordIssueResult {
  temporary_password: string | null
}

/** 创建用户响应额外带用户标识，供一次性密码弹窗展示。 */
export interface CreateUserResult extends PasswordIssueResult {
  username: string
}

/** 更新用户——对齐后端 `UpdateUserReq`（无 username / password）。 */
export interface UpdateUserReq {
  nickname: string
  email?: string | null
  phone?: string | null
  status: UserStatus
  description?: string | null
  role_ids?: string[]
  dept_id?: string | null
}

/** 用户表单值（新建 / 编辑共用）。 */
export interface UserFormValues {
  username?: string
  nickname?: string
  password?: string
  email?: string
  phone?: string
  status: UserStatus
  description?: string
  dept_id?: string
  role_ids?: string[]
}

/** 桌面表格：在视图入参上再加分页与状态开关。 */
export interface UserTableProps extends UserListViewProps {
  total: number
  page: number
  pageSize: number
  statusPendingId?: string
  onStatusChange: (user: UserListItem, status: UserStatus) => void
  onPageChange: (page: number, pageSize: number) => void
}

/** 工具栏：筛选值 + 变更回调（回调 patch 的键即 URL query 参数名）。 */
export interface UserToolbarProps {
  keyword: string
  status?: UserStatus
  userType?: UserType
  needChangePassword?: boolean
  recycleMode: boolean
  onChange: (patch: Record<string, string | undefined>) => void
  onRecycleModeChange: (recycleMode: boolean) => void
  onCreate: () => void
}
