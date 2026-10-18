import { ActionSheet, ErrorBlock, List, Tag } from 'antd-mobile'
import { useState } from 'react'

import { STATUS_LABELS } from '../../../constants'
import type { Status } from '../../../types'
import type { Dept, DeptTreeNode } from '../../types'

/** antd-mobile Tag 的预设色系（与 antd 不同，移动端就近映射）。 */
const MOBILE_STATUS_COLORS: Record<Status, 'success' | 'default'> = {
  active: 'success',
  disabled: 'default',
}

interface Props {
  nodes: DeptTreeNode[]
  loading: boolean
  error: Error | null
  onView: (dept: Dept) => void
  onEdit: (dept: Dept) => void
  onCreateChild: (parentId: string) => void
  onDelete: (dept: Dept) => void
}

interface FlatRow {
  node: DeptTreeNode
  depth: number
}

function flatten(nodes: DeptTreeNode[], depth = 0): FlatRow[] {
  return nodes.flatMap((node) => [{ node, depth }, ...flatten(node.children ?? [], depth + 1)])
}

/**
 * 【分叉档 · 移动】部门树列表：按层级缩进展平；点项弹 ActionSheet 出操作。
 * 与 desktop/DeptTable 同源数据，取数在 DeptPage。
 */
export function DeptTreeList({
  nodes,
  loading,
  error,
  onView,
  onEdit,
  onCreateChild,
  onDelete,
}: Props) {
  const [active, setActive] = useState<DeptTreeNode | null>(null)
  const rows = flatten(nodes)

  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <>
      <List>
        {rows.map(({ node, depth }) => (
          <List.Item
            key={node.id}
            style={{ paddingLeft: 12 + depth * 16 }}
            onClick={() => setActive(node)}
            extra={<Tag color={MOBILE_STATUS_COLORS[node.status]}>{STATUS_LABELS[node.status]}</Tag>}
          >
            {node.name}
          </List.Item>
        ))}
        {loading && <List.Item>加载中…</List.Item>}
        {!loading && rows.length === 0 && <List.Item>暂无部门</List.Item>}
      </List>

      <ActionSheet
        visible={active !== null}
        cancelText="取消"
        onClose={() => setActive(null)}
        actions={[
          { key: 'view', text: '查看' },
          { key: 'child', text: '新增子部门' },
          { key: 'edit', text: '编辑' },
          { key: 'delete', text: '删除', danger: true },
        ]}
        onAction={(action) => {
          if (!active) return
          const target = active
          setActive(null)
          if (action.key === 'view') onView(target)
          else if (action.key === 'child') onCreateChild(target.id)
          else if (action.key === 'edit') onEdit(target)
          else if (action.key === 'delete') onDelete(target)
        }}
      />
    </>
  )
}
