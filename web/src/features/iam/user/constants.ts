import type { UserStatus, UserType } from './types'

/** 状态 → 中文（对齐后端 `StatusEnum`）。 */
export const STATUS_LABELS: Record<UserStatus, string> = {
  active: '启用',
  disabled: '禁用',
  deleted: '已删除',
}

/** 用户类型 → 中文（对齐后端 `UserTypeEnum`）。 */
export const USER_TYPE_LABELS: Record<UserType, string> = {
  admin_created: '管理员创建',
  self_registered: '自主注册',
  system: '系统用户',
  super_admin: '超级管理员',
}

export const STATUS_OPTIONS = (Object.keys(STATUS_LABELS) as UserStatus[]).map((value) => ({
  value,
  label: STATUS_LABELS[value],
}))

export const USER_TYPE_OPTIONS = (Object.keys(USER_TYPE_LABELS) as UserType[]).map((value) => ({
  value,
  label: USER_TYPE_LABELS[value],
}))
