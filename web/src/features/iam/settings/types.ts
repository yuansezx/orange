import type { SessionItem } from '../session/types'
import type { DeptRef, Status } from '../types'
import type { RoleRef, UserType } from '../user/types'

/** 自助资料——对齐后端 `MyProfileResp`（不含审计操作人与数据范围）。 */
export interface MyProfile {
  user_id: string
  username: string
  nickname: string
  email: string | null
  phone: string | null
  user_type: UserType
  status: Status
  description: string | null
  dept: DeptRef | null
  roles: RoleRef[]
  created_at: string
  updated_at: string | null
  password_updated_at: string | null
  need_change_password: boolean
  avatar_url: string | null
}

/** 自助资料更新——对齐后端 `UpdateMyProfileReq`（PUT 完整替换）。 */
export interface UpdateMyProfileReq {
  nickname: string
  email: string | null
  phone: string | null
}

/** 自助在线设备——在会话视图上标记当前设备。 */
export interface MySession extends SessionItem {
  is_current: boolean
}
