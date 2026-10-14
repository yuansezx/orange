import { Alert, Button, Space, Table, Tag } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'
import { useMemo, useState } from 'react'
import type { Key } from 'react'

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
    { title: '部门名称', dataIndex: 'name' },
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
      width: 220,
      render: (_, record) => (
        <Space size={4}>
          <Button type="link" size="small" onClick={() => onEdit(record)}>
            编辑
          </Button>
          <Button type="link" size="small" onClick={() => onCreateChild(record.id)}>
            新增子部门
          </Button>
          <Button type="link" size="small" danger onClick={() => onDelete(record)}>
            删除
          </Button>
        </Space>
      ),
    },
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
