import { TreeSelect } from 'antd'
import { useEffect, useMemo } from 'react'

import { useVisibleDepts } from '../dept/hooks/useVisibleDepts'
import { buildDeptTreeData, collectDeptIds } from './deptTree'

interface Props {
  value?: string[]
  onChange?: (value: string[]) => void
  placeholder?: string
  disabled?: boolean
}

/**
 * 部门多选（树勾选）——角色「自定义数据范围」与 API Key CUSTOM 范围共用。
 * 取「当前用户可见部门」精简树（登录即可，不要求 `iam:dept:read`）。
 * `SHOW_CHILD`：勾父节点 → 值取其实叶子部门 id（「就是这些部门」的最字面语义）。
 */
export function DeptTreeMultiSelect({
  value,
  onChange,
  placeholder = '选择部门',
  disabled,
}: Props) {
  const selected = useMemo(() => value ?? [], [value])
  const { data, isLoading, isSuccess } = useVisibleDepts()
  const known = useMemo(() => collectDeptIds(data ?? []), [data])

  // 可见范围收窄后，历史值里已不可见的部门会被后端拒绝；加载成功后剔除（只会收窄）。
  useEffect(() => {
    if (!isSuccess) return
    const filtered = selected.filter((id) => known.has(id))
    if (filtered.length !== selected.length) onChange?.(filtered)
  }, [isSuccess, known, selected, onChange])

  const treeData = useMemo(() => {
    const placeholders = selected
      .filter((id) => !known.has(id))
      .map((id) => ({ value: id, title: `部门 ${id.slice(0, 8)}` }))
    return [...buildDeptTreeData(data ?? []), ...placeholders]
  }, [data, selected, known])

  return (
    <TreeSelect
      value={value}
      onChange={(next) => onChange?.((next as string[] | undefined) ?? [])}
      treeData={treeData}
      treeCheckable
      multiple
      allowClear
      showCheckedStrategy={TreeSelect.SHOW_CHILD}
      placeholder={placeholder}
      disabled={disabled}
      loading={isLoading}
      showSearch
      treeNodeFilterProp="title"
      style={{ width: '100%' }}
    />
  )
}
