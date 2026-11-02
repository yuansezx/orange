import { TreeSelect } from 'antd'

import { useDeptTree } from '../dept/hooks/useDeptTree'
import { buildDeptTreeData } from './deptTree'

interface Props {
  value?: string[]
  onChange?: (value: string[]) => void
  placeholder?: string
  disabled?: boolean
}

/**
 * 部门多选（树勾选）——用于角色的「自定义数据范围」。
 * 自带部门树取数（与其它部门选择器共用 `['dept-tree']`）。
 * `SHOW_CHILD`：勾父节点 → 值取其实叶子部门 id（「就是这些部门」的最字面语义）。
 */
export function DeptTreeMultiSelect({
  value,
  onChange,
  placeholder = '选择部门',
  disabled,
}: Props) {
  const { data, isLoading } = useDeptTree()

  return (
    <TreeSelect
      value={value}
      onChange={(next) => onChange?.((next as string[] | undefined) ?? [])}
      treeData={buildDeptTreeData(data ?? [])}
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
