import { Descriptions } from 'antd'
import dayjs from 'dayjs'
import type { ReactNode } from 'react'

import type { AuditFields } from '../types'

/** 「时间 · 人」一行文本；人或时间缺省 → '-'。 */
function stamp(at: string | null, nickname: string | null, username: string | null): string {
  if (!at) return '-'
  const who = nickname || username
  return who ? `${dayjs(at).format('YYYY-MM-DD HH:mm')} · ${who}` : dayjs(at).format('YYYY-MM-DD HH:mm')
}

/**
 * 审计三段（创建 / 更新 / 删除）——返回 `Descriptions.Item` 数组。
 * 供 `Descriptions` 直接展开（`{...auditItems(x)}` 不可，用 `{auditItems(x)}`，antd 会摊平数组）。
 */
export function auditItems(audit: AuditFields): ReactNode[] {
  return [
    <Descriptions.Item key="audit-created" label="创建">
      {stamp(audit.created_at, audit.created_by_nickname, audit.created_by_username)}
    </Descriptions.Item>,
    <Descriptions.Item key="audit-updated" label="更新">
      {stamp(audit.updated_at, audit.updated_by_nickname, audit.updated_by_username)}
    </Descriptions.Item>,
    <Descriptions.Item key="audit-deleted" label="删除">
      {stamp(audit.deleted_at, audit.deleted_by_nickname, audit.deleted_by_username)}
    </Descriptions.Item>,
  ]
}
