import type { PageQuery } from '@shared/api'

/** 对齐后端 UserTypeEnum。 */
export type UserType = 'admin_created' | 'self_registered' | 'system' | 'super_admin'

/** 对齐后端 StatusEnum。 */
export type UserStatus = 'active' | 'disabled' | 'deleted'

/** 用户列表读模型——字段对齐后端 UserResp。 */
export interface UserListItem {
  id: string
  username: string
  nickname: string
  email: string | null
  phone: string | null
  user_type: UserType
  status: UserStatus
  description: string | null
  dept_id: string | null
  created_at: string
}

/** 列表查询参数——对齐后端 GetUsersReq。 */
export interface GetUsersQuery extends PageQuery {
  keyword?: string
  user_type?: UserType
  status?: UserStatus
  dept_id?: string
}

/** 列表视图两端的公共入参——数据在 UserPage 取好后下发，视图只负责渲染。 */
export interface UserListViewProps {
  users: UserListItem[]
  loading: boolean
  error: Error | null
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
