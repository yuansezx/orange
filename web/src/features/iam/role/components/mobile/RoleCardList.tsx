import { ActionSheet, ErrorBlock, List, Tag } from 'antd-mobile'
import { useState } from 'react'

import { DATA_SCOPE_LABELS, STATUS_LABELS } from '../../../constants'
import type { Status } from '../../../types'
import type { RoleListItem } from '../../types'

/** antd-mobile Tag 的预设色系（与 antd 不同，移动端就近映射）。 */
const MOBILE_STATUS_COLORS: Record<Status, 'success' | 'default'> = {
  active: 'success',
  disabled: 'default',
}

interface Props {
  roles: RoleListItem[]
  loading: boolean
  error: Error | null
  onView: (role: RoleListItem) => void
  onEdit: (role: RoleListItem) => void
  onDelete: (role: RoleListItem) => void
}

/** 【分叉档 · 移动】角色卡片列表；点项弹 ActionSheet 出操作（查看/编辑/删除）。 */
export function RoleCardList({ roles, loading, error, onView, onEdit, onDelete }: Props) {
  const [active, setActive] = useState<RoleListItem | null>(null)

  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <>
      <List>
        {roles.map((role) => (
          <List.Item
            key={role.id}
            onClick={() => setActive(role)}
            description={`${role.code} · ${DATA_SCOPE_LABELS[role.data_scope]} · ${
              role.created_by?.username ?? '-'
            }`}
            extra={<Tag color={MOBILE_STATUS_COLORS[role.status]}>{STATUS_LABELS[role.status]}</Tag>}
          >
            {role.name}
          </List.Item>
        ))}
        {loading && <List.Item>加载中…</List.Item>}
        {!loading && roles.length === 0 && <List.Item>暂无角色</List.Item>}
      </List>

      <ActionSheet
        visible={active !== null}
        cancelText="取消"
        onClose={() => setActive(null)}
        actions={[
          { key: 'view', text: '查看' },
          { key: 'edit', text: '编辑' },
          { key: 'delete', text: '删除', danger: true },
        ]}
        onAction={(action) => {
          if (!active) return
          const target = active
          setActive(null)
          if (action.key === 'view') onView(target)
          else if (action.key === 'edit') onEdit(target)
          else if (action.key === 'delete') onDelete(target)
        }}
      />
    </>
  )
}
