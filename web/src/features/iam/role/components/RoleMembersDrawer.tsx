import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { Alert, Button, Input, Space, Spin, Table, Tag } from 'antd'
import type { TableProps } from 'antd'
import { Checkbox, List } from 'antd-mobile'
import { useState } from 'react'

import { Platform } from '@shared/platform'

import { ManageDrawer } from '../../components/ManageDrawer'
import { STATUS_LABELS } from '../../constants'
import { USER_TYPE_LABELS } from '../../user/constants'
import { getRoleCandidates } from '../api/roleApi'
import { useRoleMutations } from '../hooks/useRoleMutations'
import type { RoleCandidateUser, RoleListItem } from '../types'

const PAGE_SIZE = 20

interface Props {
  role: RoleListItem
  onClose: () => void
}

/**
 * 角色成员管理——Drawer + 候选用户表格（分页/搜索）。
 * 每行带 `selected` 标记；勾选变化在本地累积成 add/remove，保存走增量 PATCH。
 */
export function RoleMembersDrawer({ role, onClose }: Props) {
  const [searchText, setSearchText] = useState('')
  const [keyword, setKeyword] = useState('')
  const [page, setPage] = useState(1)
  const [pending, setPending] = useState<Map<string, boolean>>(new Map())

  const { data, isLoading, error } = useQuery({
    queryKey: ['role-candidates', role.id, keyword, page],
    queryFn: () =>
      getRoleCandidates(role.id, {
        keyword: keyword || undefined,
        page,
        page_size: PAGE_SIZE,
      }),
    placeholderData: keepPreviousData,
  })
  const { patchMembers } = useRoleMutations()

  const rows = data?.data ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const isSelected = (row: RoleCandidateUser) => pending.get(row.id) ?? row.selected

  const applyPageKeys = (keys: string[]) => {
    setPending((prev) => {
      const next = new Map(prev)
      for (const row of rows) {
        const checked = keys.includes(row.id)
        if (checked !== row.selected) next.set(row.id, checked)
        else next.delete(row.id)
      }
      return next
    })
  }

  const toggleOne = (row: RoleCandidateUser, checked: boolean) => {
    setPending((prev) => {
      const next = new Map(prev)
      if (checked !== row.selected) next.set(row.id, checked)
      else next.delete(row.id)
      return next
    })
  }

  const add = [...pending].filter(([, selected]) => selected).map(([id]) => id)
  const remove = [...pending].filter(([, selected]) => !selected).map(([id]) => id)
  const selectedKeys = rows.filter(isSelected).map((row) => row.id)

  const handleSave = async () => {
    if (!add.length && !remove.length) {
      onClose()
      return
    }
    try {
      await patchMembers.mutateAsync({
        id: role.id,
        body: { add_user_ids: add, remove_user_ids: remove },
      })
      onClose()
    } catch {
      // 错误提示由 mutation 统一处理，抽屉保留以便重试
    }
  }

  const columns: TableProps<RoleCandidateUser>['columns'] = [
    { title: '用户名', dataIndex: 'username', width: 180 },
    { title: '昵称', dataIndex: 'nickname' },
    {
      title: '类型',
      dataIndex: 'user_type',
      width: 120,
      render: (value: RoleCandidateUser['user_type']) => USER_TYPE_LABELS[value] ?? value,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (value: RoleCandidateUser['status']) => (
        <Tag color={value === 'active' ? 'success' : 'default'}>{STATUS_LABELS[value]}</Tag>
      ),
    },
  ]

  return (
    <ManageDrawer open width={760} title={`管理成员 · ${role.name}`} onClose={onClose}>
      <Input.Search
        allowClear
        placeholder="搜索用户名 / 昵称"
        value={searchText}
        onChange={(event) => setSearchText(event.target.value)}
        onSearch={(value) => {
          setKeyword(value.trim())
          setPage(1)
        }}
        style={{ marginBottom: 12 }}
      />

      {isLoading ? (
        <Spin />
      ) : error ? (
        <Alert type="error" showIcon message={error.message} />
      ) : (
        <>
          <Platform
            desktop={
              <Table<RoleCandidateUser>
                rowKey="id"
                size="small"
                columns={columns}
                dataSource={rows}
                scroll={{ y: 420 }}
                pagination={{
                  current: page,
                  pageSize: PAGE_SIZE,
                  total,
                  showSizeChanger: false,
                  onChange: (nextPage) => setPage(nextPage),
                }}
                rowSelection={{
                  selectedRowKeys: selectedKeys,
                  onChange: (keys) => applyPageKeys(keys.map(String)),
                }}
              />
            }
            mobile={
              <>
                <List>
                  {rows.map((row) => (
                    <List.Item
                      key={row.id}
                      prefix={
                        <Checkbox
                          checked={isSelected(row)}
                          onChange={(checked) => toggleOne(row, checked)}
                        />
                      }
                      description={`${row.nickname} · ${USER_TYPE_LABELS[row.user_type]} · ${
                        STATUS_LABELS[row.status]
                      }`}
                    >
                      {row.username}
                    </List.Item>
                  ))}
                  {rows.length === 0 && <List.Item>暂无匹配用户</List.Item>}
                </List>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginTop: 12,
                  }}
                >
                  <Button size="small" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                    上一页
                  </Button>
                  <span>
                    第 {page} / {totalPages} 页
                  </span>
                  <Button
                    size="small"
                    disabled={page >= totalPages}
                    onClick={() => setPage(page + 1)}
                  >
                    下一页
                  </Button>
                </div>
              </>
            }
          />

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: 16,
            }}
          >
            <span>
              新增 {add.length} · 移除 {remove.length}
            </span>
            <Space>
              <Button onClick={onClose}>取消</Button>
              <Button type="primary" loading={patchMembers.isPending} onClick={handleSave}>
                保存
              </Button>
            </Space>
          </div>
        </>
      )}
    </ManageDrawer>
  )
}
