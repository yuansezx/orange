import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { Alert, App, Button, Input, Segmented, Space, Spin, Table, Tag } from 'antd'
import type { TableProps } from 'antd'
import { Checkbox, List } from 'antd-mobile'
import { useState } from 'react'

import { Platform } from '@shared/platform'

import { ManageDrawer } from '../../components/ManageDrawer'
import { STATUS_LABELS } from '../../constants'
import { USER_TYPE_LABELS } from '../../user/constants'
import { getRoleCandidates, getRoleMembers } from '../api/roleApi'
import { useRoleMutations } from '../hooks/useRoleMutations'
import type { RoleCandidateUser, RoleListItem, RoleMember } from '../types'

const PAGE_SIZE = 20

type Mode = 'read' | 'manage'

interface Props {
  role: RoleListItem
  /** `iam:user_role:assign` && `iam:user:read`；入口本身已要求 `user_role:read`。 */
  canManage: boolean
  onClose: () => void
}

/**
 * 角色成员入口：查看 / 管理切换（正常-回收站同款 Segmented）。
 * 只读成员 = 未删除的角色分配（含用户自助停用的分配）。
 */
export function RoleMembersDrawer({ role, canManage, onClose }: Props) {
  const { modal } = App.useApp()
  const [mode, setMode] = useState<Mode>('read')
  const [pending, setPending] = useState<Map<string, boolean>>(new Map())

  const changeMode = (next: Mode) => {
    if (next === 'manage') {
      setMode('manage')
      return
    }
    if (pending.size === 0) {
      setMode('read')
      return
    }
    modal.confirm({
      title: '放弃未保存的更改？',
      content: '切换到查看会丢弃本次增删。',
      okButtonProps: { danger: true },
      onOk: () => {
        setPending(new Map())
        setMode('read')
      },
    })
  }

  return (
    <ManageDrawer open width={860} title={`成员 · ${role.name}`} onClose={onClose}>
      {canManage && (
        <Segmented
          value={mode}
          options={[
            { label: '查看', value: 'read' },
            { label: '管理', value: 'manage' },
          ]}
          onChange={(next) => changeMode(next as Mode)}
          style={{ marginBottom: 12 }}
        />
      )}
      {mode === 'read' ? (
        <RoleMembersRead role={role} onClose={onClose} />
      ) : (
        <RoleMembersManage
          role={role}
          pending={pending}
          setPending={setPending}
          onClose={onClose}
        />
      )}
    </ManageDrawer>
  )
}

// ---------------- 只读 ----------------

interface ReadProps {
  role: RoleListItem
  onClose: () => void
}

function RoleMembersRead({ role, onClose }: ReadProps) {
  const [searchText, setSearchText] = useState('')
  const [keyword, setKeyword] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading, error } = useQuery({
    queryKey: ['role-members', role.id, keyword, page],
    queryFn: () =>
      getRoleMembers(role.id, {
        keyword: keyword || undefined,
        page,
        page_size: PAGE_SIZE,
      }),
    placeholderData: keepPreviousData,
  })

  const rows = data?.data ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const columns: TableProps<RoleMember>['columns'] = [
    { title: '用户名', dataIndex: 'username', width: 180 },
    { title: '昵称', dataIndex: 'nickname' },
    {
      title: '类型',
      dataIndex: 'user_type',
      width: 120,
      render: (value: RoleMember['user_type']) => USER_TYPE_LABELS[value] ?? value,
    },
    {
      title: '用户状态',
      dataIndex: 'status',
      width: 100,
      render: (value: RoleMember['status']) => (
        <Tag color={value === 'active' ? 'success' : 'default'}>{STATUS_LABELS[value]}</Tag>
      ),
    },
    {
      title: '分配状态',
      dataIndex: 'assignment_status',
      width: 100,
      render: (value: RoleMember['assignment_status']) => (
        <Tag color={value === 'active' ? 'success' : 'default'}>{STATUS_LABELS[value]}</Tag>
      ),
    },
  ]

  return (
    <div>
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
              <Table<RoleMember>
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
              />
            }
            mobile={
              <>
                <List>
                  {rows.map((member) => (
                    <List.Item
                      key={member.id}
                      description={`${member.nickname} · ${USER_TYPE_LABELS[member.user_type]} · 用户${
                        STATUS_LABELS[member.status]
                      } · 分配${STATUS_LABELS[member.assignment_status]}`}
                    >
                      {member.username}
                    </List.Item>
                  ))}
                  {rows.length === 0 && <List.Item>暂无成员</List.Item>}
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
            <span>共 {total} 人</span>
            <Button onClick={onClose}>关闭</Button>
          </div>
        </>
      )}
    </div>
  )
}

// ---------------- 管理 ----------------

interface ManageProps {
  role: RoleListItem
  pending: Map<string, boolean>
  setPending: (pending: Map<string, boolean>) => void
  onClose: () => void
}

function RoleMembersManage({ role, pending, setPending, onClose }: ManageProps) {
  const [searchText, setSearchText] = useState('')
  const [keyword, setKeyword] = useState('')
  const [page, setPage] = useState(1)

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
    const next = new Map(pending)
    for (const row of rows) {
      const checked = keys.includes(row.id)
      if (checked !== row.selected) next.set(row.id, checked)
      else next.delete(row.id)
    }
    setPending(next)
  }

  const toggleOne = (row: RoleCandidateUser, checked: boolean) => {
    const next = new Map(pending)
    if (checked !== row.selected) next.set(row.id, checked)
    else next.delete(row.id)
    setPending(next)
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
    <div>
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
    </div>
  )
}
