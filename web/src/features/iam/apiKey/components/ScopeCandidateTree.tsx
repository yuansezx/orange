import { Empty, Spin, Tree } from 'antd'
import type { Key } from 'react'
import { useEffect, useMemo, useState } from 'react'

import { useScopeCandidates } from '../hooks/useApiKeys'
import type { ScopeCandidate } from '../types'

interface TreeNode {
  key: string
  title: string
  isLeaf?: boolean
  children?: TreeNode[]
}

/** 候选（按资源分组）→ 模块 → 资源 → 权限码树；同时收集叶子码集合。 */
function buildTree(candidates: ScopeCandidate[]): {
  treeData: TreeNode[]
  leafCodes: Set<string>
} {
  const leafCodes = new Set<string>()
  const modules = new Map<string, ScopeCandidate[]>()
  for (const candidate of candidates) {
    const list = modules.get(candidate.module) ?? []
    list.push(candidate)
    modules.set(candidate.module, list)
  }

  const treeData = [...modules.entries()].map(([module, resources]) => ({
    key: `module:${module}`,
    title: module,
    children: resources.map((resource) => ({
      key: `resource:${module}:${resource.resource}`,
      title: resource.name,
      children: resource.permissions.map((permission) => {
        leafCodes.add(permission.code)
        return { key: permission.code, title: permission.name, isLeaf: true }
      }),
    })),
  }))
  return { treeData, leafCodes }
}

function collectKeys(nodes: TreeNode[]): Key[] {
  return nodes.flatMap((node) => [node.key, ...collectKeys(node.children ?? [])])
}

interface Props {
  value?: string[]
  onChange?: (codes: string[]) => void
}

/**
 * API Key 权限范围树——**值为权限码集合**（与角色权限树的 id 语义不同）。
 * 候选由后端按「当前用户有效权限」收窄；父节点勾选态由 antd 依叶子派生。
 */
export function ScopeCandidateTree({ value = [], onChange }: Props) {
  const { data, isLoading } = useScopeCandidates()
  const [collapsed, setCollapsed] = useState<Set<Key>>(new Set())

  const { treeData, leafCodes } = useMemo(
    () =>
      data
        ? buildTree(data)
        : { treeData: [] as TreeNode[], leafCodes: new Set<string>() },
    [data],
  )
  const allKeys = useMemo(() => collectKeys(treeData), [treeData])
  const expandedKeys = allKeys.filter((key) => !collapsed.has(key))

  // 用户失权后候选树会收窄；编辑旧 key 时把已不在候选里的权限码剔掉，避免保存被后端拒绝。
  useEffect(() => {
    if (!data) return
    const filtered = value.filter((code) => leafCodes.has(code))
    if (filtered.length !== value.length) onChange?.(filtered)
  }, [data, leafCodes, value, onChange])

  if (isLoading) return <Spin />
  if (treeData.length === 0) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无可分配权限" />
  }

  return (
    <Tree
      checkable
      selectable={false}
      treeData={treeData}
      checkedKeys={value}
      onCheck={(checked) => {
        const keys = Array.isArray(checked) ? checked : checked.checked
        onChange?.(keys.map(String).filter((key) => leafCodes.has(key)))
      }}
      expandedKeys={expandedKeys}
      onExpand={(keys) => setCollapsed(new Set(allKeys.filter((key) => !keys.includes(key))))}
    />
  )
}
