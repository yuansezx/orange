import { Alert, Button, Space, Table, Tag, Tooltip } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'
import { useMemo, useState } from 'react'
import type { Key } from 'react'

import { IconBuildingPlus, IconEdit, IconTrash } from '@shared/ui'

import { STATUS_COLORS, STATUS_LABELS } from '../../../constants'
import type { Dept, DeptTreeNode } from '../../types'

interface Props {
  nodes: DeptTreeNode[]
  loading: boolean
  error: Error | null
  onEdit: (dept: Dept) => void
  onCreateChild: (parentId: string) => void
  onDelete: (dept: Dept) => void
}

function collectIds(nodes: DeptTreeNode[]): Key[] {
  return nodes.flatMap((node) => [node.id, ...collectIds(node.children ?? [])])
}

/**
 * 【分叉档 · 桌面】部门树表格（antd `Table` 原生支持 `children` 递归展开）。
 * 只负责渲染 + 操作回调；取数与弹层在 DeptPage。
 */
export function DeptTable({ nodes, loading, error, onEdit, onCreateChild, onDelete }: Props) {
  // 受控展开：默认全展开（defaultExpandAllRows 对异步数据不生效）。
  // 只记「被用户折叠」的节点，展开态由 全部节点 - 已折叠 派生——异步数据到达/新增节点均自动展开，无需 effect。
  const [collapsed, setCollapsed] = useState<Set<Key>>(new Set())
  const allIds = useMemo(() => collectIds(nodes), [nodes])
  const expandedKeys = allIds.filter((id) => !collapsed.has(id))

  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const columns: TableProps<DeptTreeNode>['columns'] = [
    { title: '部门名称', dataIndex: 'name', width: 320, ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (value: Dept['status']) => <Tag color={STATUS_COLORS[value]}>{STATUS_LABELS[value]}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (value: string) => (value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-'),
    },
    {
      title: '操作',
      width: 160,
      render: (_, record) => (
        <Space size={8}>
          <Tooltip title="编辑">
            <Button type="text" icon={<IconEdit size={16} />} onClick={() => onEdit(record)} />
          </Tooltip>
          <Tooltip title="新增子部门">
            <Button
              type="text"
              icon={<IconBuildingPlus size={16} />}
              onClick={() => onCreateChild(record.id)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button type="text" danger icon={<IconTrash size={16} />} onClick={() => onDelete(record)} />
          </Tooltip>
        </Space>
      ),
    },
    // 空列吸收剩余宽度：避免部门树随容器被拉宽、把「操作」挤窄
    { key: 'spacer', title: '', render: () => null },
  ]

  return (
    <Table<DeptTreeNode>
      rowKey="id"
      loading={loading}
      columns={columns}
      dataSource={nodes}
      pagination={false}
      expandable={{
        expandedRowKeys: expandedKeys,
        onExpandedRowsChange: (keys) => {
          const expanded = new Set(keys)
          setCollapsed(new Set(allIds.filter((id) => !expanded.has(id))))
        },
      }}
    />
  )
}
