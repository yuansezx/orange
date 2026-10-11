/** 登录请求/响应（对齐后端 `LoginIn` / `LoginOut`）。 */
export interface LoginReq {
  username: string
  password: string
}

export interface LoginResp {
  access_token: string
  token_type: string
  /** 有效期（秒） */
  expires_in: number
  need_change_password: boolean
}

/** 用户类型（对齐后端 `UserTypeEnum`）。 */
export type UserType = 'admin_created' | 'self_registered' | 'system' | 'super_admin'

/** 角色精简视图（对齐后端 `RoleSummary`，单值 VO 已裸值化）。 */
export interface RoleSummary {
  id: string
  code: string
  name: string
}

/** 当前用户（对齐后端 `CurrentUser` 的线上形状）。 */
export interface CurrentUser {
  user_id: string
  username: string
  nickname: string
  user_type: UserType
  roles: RoleSummary[] | null
  dept_id: string | null
  permission_codes: string[] | null
}
