import type { DataScope, Status } from './types'

/** 状态 → 中文（对齐后端 `StatusEnum`；iam 各资源共用）。 */
export const STATUS_LABELS: Record<Status, string> = {
  active: '启用',
  disabled: '停用',
}

/** 状态 → **antd** Tag 预设色（antd-mobile 色系不同，移动端各自就近映射）。 */
export const STATUS_COLORS: Record<Status, string> = {
  active: 'success',
  disabled: 'default',
}

export const STATUS_OPTIONS = (Object.keys(STATUS_LABELS) as Status[]).map((value) => ({
  value,
  label: STATUS_LABELS[value],
}))

/** 数据范围 → 中文（对齐后端 `DataScopeEnum`）。 */
export const DATA_SCOPE_LABELS: Record<DataScope, string> = {
  all: '全部数据',
  dept: '本部门',
  dept_and_child: '本部门及下级',
  custom: '自定义部门',
  self: '仅本人',
}

export const DATA_SCOPE_OPTIONS = (Object.keys(DATA_SCOPE_LABELS) as DataScope[]).map((value) => ({
  value,
  label: DATA_SCOPE_LABELS[value],
}))
