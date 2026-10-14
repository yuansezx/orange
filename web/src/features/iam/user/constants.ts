import type { UserType } from './types'

// 状态标签为 iam 资源共用，收敛到模块级单源（见 features/iam/constants.ts）
export { STATUS_LABELS, STATUS_OPTIONS } from '../constants'

/** 用户类型 → 中文（对齐后端 `UserTypeEnum`）。 */
export const USER_TYPE_LABELS: Record<UserType, string> = {
  admin_created: '管理员创建',
  self_registered: '自主注册',
  system: '系统用户',
  super_admin: '超级管理员',
}

export const USER_TYPE_OPTIONS = (Object.keys(USER_TYPE_LABELS) as UserType[]).map((value) => ({
  value,
  label: USER_TYPE_LABELS[value],
}))
