import type { Status } from './types'

/** 状态 → 中文（对齐后端 `StatusEnum`；iam 各资源共用）。 */
export const STATUS_LABELS: Record<Status, string> = {
  active: '启用',
  disabled: '禁用',
  deleted: '已删除',
}

/** 状态 → **antd** Tag 预设色（antd-mobile 色系不同，移动端各自就近映射）。 */
export const STATUS_COLORS: Record<Status, string> = {
  active: 'success',
  disabled: 'default',
  deleted: 'error',
}

export const STATUS_OPTIONS = (Object.keys(STATUS_LABELS) as Status[]).map((value) => ({
  value,
  label: STATUS_LABELS[value],
}))
