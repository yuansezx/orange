import { ActionSheet, ErrorBlock, List, Tag } from 'antd-mobile'
import dayjs from 'dayjs'
import { useState } from 'react'

import { STATUS_LABELS } from '../../../constants'
import type { Status } from '../../../types'
import type { DeptListItem } from '../../types'

const MOBILE_STATUS_COLORS: Record<Status, 'success' | 'default'> = {
  active: 'success',
  disabled: 'default',
}

interface Props {
  depts: DeptListItem[]
  loading: boolean
  error: Error | null
  onView: (dept: DeptListItem) => void
  onRestore: (dept: DeptListItem) => void
  onHardDelete: (dept: DeptListItem) => void
}

/** 【分叉档 · 移动】回收站扁平卡片列表：点项弹查看 / 恢复 / 彻底删除。 */
export function DeletedDeptCardList({ depts, loading, error, onView, onRestore, onHardDelete }: Props) {
  const [active, setActive] = useState<DeptListItem | null>(null)

  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <>
      <List header="回收站">
        {depts.map((dept) => (
          <List.Item
            key={dept.id}
            onClick={() => setActive(dept)}
            description={`删除于 ${dept.deleted_at ? dayjs(dept.deleted_at).format('YYYY-MM-DD') : '-'} · ${
              dept.deleted_by?.username ?? '-'
            }`}
            extra={<Tag color={MOBILE_STATUS_COLORS[dept.status]}>{STATUS_LABELS[dept.status]}</Tag>}
          >
            {dept.name}
          </List.Item>
        ))}
        {loading && <List.Item>加载中…</List.Item>}
        {!loading && depts.length === 0 && <List.Item>回收站为空</List.Item>}
      </List>

      <ActionSheet
        visible={active !== null}
        cancelText="取消"
        onClose={() => setActive(null)}
        actions={[
          { key: 'view', text: '查看' },
          { key: 'restore', text: '恢复' },
          { key: 'hardDelete', text: '彻底删除', danger: true },
        ]}
        onAction={(action) => {
          if (!active) return
          const target = active
          setActive(null)
          if (action.key === 'view') onView(target)
          else if (action.key === 'restore') onRestore(target)
          else if (action.key === 'hardDelete') onHardDelete(target)
        }}
      />
    </>
  )
}
