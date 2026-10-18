import { Descriptions } from 'antd'
import dayjs from 'dayjs'
import type { ReactNode } from 'react'

import type { AuditFields, OperatorRef } from '../types'

/** 「时间 · 用户名」；操作人已硬删 → 「已删除用户」；时间缺省 → '-'。 */
function stamp(at: string | null, operator: OperatorRef | null): string {
  if (!at) return '-'
  const time = dayjs(at).format('YYYY-MM-DD HH:mm')
  return operator ? `${time} · ${operator.username ?? '已删除用户'}` : time
}

/**
 * 审计三段（创建 / 更新 / 删除）——返回 `Descriptions.Item` 数组。
 * 供 `Descriptions` 直接展开（`{...auditItems(x)}` 不可，用 `{auditItems(x)}`，antd 会摊平数组）。
 */
export function auditItems(audit: AuditFields): ReactNode[] {
  return [
    <Descriptions.Item key="audit-created" label="创建">
      {stamp(audit.created_at, audit.created_by)}
    </Descriptions.Item>,
    <Descriptions.Item key="audit-updated" label="更新">
      {stamp(audit.updated_at, audit.updated_by)}
    </Descriptions.Item>,
    <Descriptions.Item key="audit-deleted" label="删除">
      {stamp(audit.deleted_at, audit.deleted_by)}
    </Descriptions.Item>,
  ]
}
