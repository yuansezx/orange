import { TreeSelect } from 'antd'

import { useVisibleDepts } from '../dept/hooks/useVisibleDepts'
import { buildDeptTreeData, collectDeptIds } from './deptTree'

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
 * 取「当前用户可见部门」精简树（登录即可，不要求 `iam:dept:read`），
 * 与用户/角色/API Key 表单共用 `['dept-visible']` 缓存。
 * 出入为部门 id，可直接挂 antd `Form.Item`。
 */
export function DeptTreeSelect({
  value,
  onChange,
  excludeIds,
  placeholder = '选择部门',
  allowClear = true,
  disabled,
}: Props) {
  const { data, isLoading } = useVisibleDepts()
  const nodes = data ?? []
  const treeData = buildDeptTreeData(nodes, new Set(excludeIds ?? []))
  // 历史值已不在可见范围内时给占位节点，避免选择器显示裸 UUID
  if (value && !collectDeptIds(nodes).has(value)) {
    treeData.push({ value, title: `部门 ${value.slice(0, 8)}` })
  }

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
