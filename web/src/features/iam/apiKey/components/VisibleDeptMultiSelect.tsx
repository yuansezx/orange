import { TreeSelect } from 'antd'
import { useEffect, useMemo } from 'react'

import { buildDeptTreeData } from '../../components/deptTree'
import { useVisibleDepts } from '../hooks/useApiKeys'
import type { VisibleDeptNode } from '../types'

function collectIds(nodes: VisibleDeptNode[]): Set<string> {
  return new Set(nodes.flatMap((node) => [node.id, ...collectIds(node.children)]))
}

interface Props {
  value?: string[]
  onChange?: (ids: string[]) => void
  disabled?: boolean
}

/**
 * 自助可见部门多选（数据范围 CUSTOM 用）。
 * 历史 key 的部门若已不在当前可见范围，注入占位节点，避免编辑时显示裸 UUID。
 */
export function VisibleDeptMultiSelect({ value = [], onChange, disabled }: Props) {
  const { data = [], isLoading, isSuccess } = useVisibleDepts()

  // 可见范围收窄后，旧 key 里已不可见的部门会被后端拒绝；加载成功后剔除（只会收窄，不会放宽）。
  useEffect(() => {
    if (!isSuccess) return
    const known = collectIds(data)
    const filtered = value.filter((id) => known.has(id))
    if (filtered.length !== value.length) onChange?.(filtered)
  }, [isSuccess, data, value, onChange])

  const treeData = useMemo(() => {
    const known = collectIds(data)
    const placeholders = value
      .filter((id) => !known.has(id))
      .map((id) => ({ value: id, title: `部门 ${id.slice(0, 8)}` }))
    return [...buildDeptTreeData(data), ...placeholders]
  }, [data, value])

  return (
    <TreeSelect
      value={value}
      onChange={(next) => onChange?.((next as string[] | undefined) ?? [])}
      treeData={treeData}
      treeCheckable
      multiple
      allowClear
      showCheckedStrategy={TreeSelect.SHOW_CHILD}
      placeholder="选择部门"
      disabled={disabled}
      loading={isLoading}
      showSearch
      treeNodeFilterProp="title"
      style={{ width: '100%' }}
    />
  )
}
