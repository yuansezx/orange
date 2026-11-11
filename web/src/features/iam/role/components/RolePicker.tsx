import { Alert, Input, Table, Tag } from 'antd'
import type { TableProps } from 'antd'
import { useEffect, useRef, useState } from 'react'

import { DATA_SCOPE_LABELS, STATUS_LABELS } from '../../constants'
import { useRoles } from '../hooks/useRoles'
import type { RoleListItem } from '../types'

interface Props {
  /** 已选角色 id；跨页保留。 */
  value: string[]
  /** 同时回传已选角色行，供调用方展示名称。 */
  onChange: (ids: string[], roles: RoleListItem[]) => void
  pageSize?: number
}

/**
 * 角色选择表：服务端关键词 + 分页 + 跨页保留勾选。
 * 管理角色抽屉与新建用户的角色分配弹窗共用。
 */
export function RolePicker({ value, onChange, pageSize = 8 }: Props) {
  const [page, setPage] = useState(1)
  const [keyword, setKeyword] = useState('')
  const { data, isLoading, error } = useRoles({
    page,
    page_size: pageSize,
    keyword: keyword || undefined,
    sort_by: 'code',
    order: 'asc',
  })
  // 记住见过的行，选中项翻出当前页后仍能回传名称
  const knownRoles = useRef(new Map<string, RoleListItem>())

  useEffect(() => {
    for (const role of data?.data ?? []) knownRoles.current.set(role.id, role)
  }, [data])

  if (error) {
    return <Alert type="error" showIcon message={error.message} />
  }

  const columns: TableProps<RoleListItem>['columns'] = [
    { title: '角色标识', dataIndex: 'code', width: 160 },
    { title: '名称', dataIndex: 'name' },
    {
      title: '数据范围',
      dataIndex: 'data_scope',
      width: 140,
      render: (v: RoleListItem['data_scope']) => DATA_SCOPE_LABELS[v],
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (v: RoleListItem['status']) => (
        <Tag color={v === 'active' ? 'success' : 'default'}>{STATUS_LABELS[v]}</Tag>
      ),
    },
  ]

  return (
    <>
      <Input.Search
        allowClear
        placeholder="搜索角色标识 / 名称"
        style={{ marginBottom: 12 }}
        onSearch={(next) => {
          setKeyword(next.trim())
          setPage(1)
        }}
      />
      <Table<RoleListItem>
        rowKey="id"
        size="small"
        loading={isLoading}
        columns={columns}
        dataSource={data?.data ?? []}
        pagination={{
          current: page,
          pageSize,
          total: data?.total ?? 0,
          showSizeChanger: false,
          showTotal: (count) => `共 ${count} 条`,
          onChange: setPage,
        }}
        scroll={{ y: 360 }}
        rowSelection={{
          selectedRowKeys: value,
          preserveSelectedRowKeys: true,
          onChange: (keys) => {
            const ids = keys.map(String)
            const roles = ids
              .map((id) => knownRoles.current.get(id))
              .filter((role): role is RoleListItem => role !== undefined)
            onChange(ids, roles)
          },
        }}
      />
    </>
  )
}
