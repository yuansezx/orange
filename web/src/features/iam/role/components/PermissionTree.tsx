import { Empty, Spin, Tree } from 'antd'
import { useMemo, useState } from 'react'
import type { Key } from 'react'

import { usePermissionCatalog } from '../hooks/usePermissionCatalog'
import type { Catalog } from '../types'

interface TreeNode {
  key: string
  title: string
  disabled?: boolean
  isLeaf?: boolean
  children?: TreeNode[]
}

/** 目录（模块 → 资源 → 权限）→ 树；同时收集叶子（权限 id）集合，供勾选值过滤。 */
function buildTree(
  catalog: Catalog,
  readOnly: boolean,
): { treeData: TreeNode[]; permissionIds: Set<string> } {
  const permissionIds = new Set<string>()
  const treeData = catalog.modules.map((module) => ({
    key: `module:${module.module}`,
    title: module.module,
    disabled: readOnly,
    children: module.resources.map((resource) => ({
      key: `resource:${resource.id}`,
      title: resource.name,
      disabled: readOnly,
      children: resource.permissions.map((permission) => {
        permissionIds.add(permission.id)
        return { key: permission.id, title: permission.name, isLeaf: true, disabled: readOnly }
      }),
    })),
  }))
  return { treeData, permissionIds }
}

function collectKeys(nodes: TreeNode[]): Key[] {
  return nodes.flatMap((node) => [node.key, ...collectKeys(node.children ?? [])])
}

interface Props {
  value: string[]
  onChange?: (permissionIds: string[]) => void
  /** 只读（详情）：节点禁用，不可勾选。 */
  readOnly?: boolean
}

/**
 * 权限树（模块 → 资源 → 权限，可勾选）——**值为权限 id 集合**。
 * 父节点（模块/资源）勾选态由 antd 依叶子派生；提交时只保留权限叶子 id。
 */
export function PermissionTree({ value, onChange, readOnly = false }: Props) {
  const { data, isLoading } = usePermissionCatalog()
  // 记「被折叠」的节点，展开态由 全部节点 - 已折叠 派生（异步数据到达自动展开，无需 effect）
  const [collapsed, setCollapsed] = useState<Set<Key>>(new Set())

  const { treeData, permissionIds } = useMemo(
    () =>
      data
        ? buildTree(data, readOnly)
        : { treeData: [] as TreeNode[], permissionIds: new Set<string>() },
    [data, readOnly],
  )
  const allKeys = useMemo(() => collectKeys(treeData), [treeData])
  const expandedKeys = allKeys.filter((key) => !collapsed.has(key))

  if (isLoading) return <Spin />
  if (treeData.length === 0) return <Empty description="暂无可分配权限" />

  return (
    <Tree
      checkable
      selectable={false}
      treeData={treeData}
      checkedKeys={value}
      onCheck={(checked) => {
        const keys = Array.isArray(checked) ? checked : checked.checked
        onChange?.(keys.map(String).filter((key) => permissionIds.has(key)))
      }}
      expandedKeys={expandedKeys}
      onExpand={(keys) => setCollapsed(new Set(allKeys.filter((key) => !keys.includes(key))))}
    />
  )
}
