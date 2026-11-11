import type { TreeSelectProps } from 'antd'

/** 选择器只依赖的最小部门树形状（管理端 / 自助精简树都满足）。 */
export interface DeptTreeLikeNode {
  id: string
  name: string
  children?: DeptTreeLikeNode[]
}

type TreeNode = NonNullable<TreeSelectProps['treeData']>[number]

/** 部门树 → antd 选择器 `treeData`；`exclude` 中的节点禁用（编辑时防环）。 */
export function buildDeptTreeData(nodes: DeptTreeLikeNode[], exclude?: Set<string>): TreeNode[] {
  return nodes.map((node) => ({
    value: node.id,
    title: node.name,
    disabled: exclude?.has(node.id) ?? false,
    children: buildDeptTreeData(node.children ?? [], exclude),
  }))
}
