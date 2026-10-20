import type { SourceType } from './types'

/** 来源 → 中文（对齐后端 `SourceTypeEnum`）。 */
export const SOURCE_LABELS: Record<SourceType, string> = {
  system: '系统',
  custom: '自定义',
}

/** 来源 → **antd** Tag 预设色；移动端就近映射。 */
export const SOURCE_COLORS: Record<SourceType, string> = {
  system: 'blue',
  custom: 'green',
}
