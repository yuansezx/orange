import type { TreeSelectProps } from 'antd'

import type { DeptTreeNode } from '../dept/types'

type TreeNode = NonNullable<TreeSelectProps['treeData']>[number]

/** 部门树 → antd 选择器 `treeData`；`exclude` 中的节点禁用（编辑时防环）。 */
export function buildDeptTreeData(nodes: DeptTreeNode[], exclude?: Set<string>): TreeNode[] {
  return nodes.map((node) => ({
    value: node.id,
    title: node.name,
    disabled: exclude?.has(node.id) ?? false,
    children: buildDeptTreeData(node.children ?? [], exclude),
  }))
}
