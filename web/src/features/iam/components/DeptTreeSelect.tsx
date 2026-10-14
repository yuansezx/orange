import { TreeSelect } from 'antd'
import type { TreeSelectProps } from 'antd'

import { useDeptTree } from '../dept/hooks/useDeptTree'
import type { DeptTreeNode } from '../dept/types'

type TreeNode = NonNullable<TreeSelectProps['treeData']>[number]

function buildTreeData(nodes: DeptTreeNode[], exclude: Set<string>): TreeNode[] {
  return nodes.map((node) => ({
    value: node.id,
    title: node.name,
    disabled: exclude.has(node.id),
    children: buildTreeData(node.children ?? [], exclude),
  }))
}

interface Props {
  value?: string
  onChange?: (value?: string) => void
  /** 需禁用的节点 id（编辑时传自身及子孙，防环；后端亦校验）。 */
  excludeIds?: string[]
  placeholder?: string
  allowClear?: boolean
  disabled?: boolean
}

/**
 * 部门选择器（树）。
 * 自带部门树取数（与 dept 页共用 `['dept-tree']` 查询，TanStack 自动去重）。
 * 出入为部门 id，可直接挂 antd `Form.Item`。供部门表单 / 后续角色、用户页复用。
 */
export function DeptTreeSelect({
  value,
  onChange,
  excludeIds,
  placeholder = '选择部门',
  allowClear = true,
  disabled,
}: Props) {
  const { data, isLoading } = useDeptTree()
  const treeData = buildTreeData(data ?? [], new Set(excludeIds ?? []))

  return (
    <TreeSelect
      value={value}
      onChange={onChange}
      treeData={treeData}
      placeholder={placeholder}
      allowClear={allowClear}
      disabled={disabled}
      loading={isLoading}
      showSearch
      treeNodeFilterProp="title"
      style={{ width: '100%' }}
    />
  )
}
