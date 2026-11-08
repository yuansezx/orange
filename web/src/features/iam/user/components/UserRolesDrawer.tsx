import { useQuery } from '@tanstack/react-query'
import { Alert, Button, Input, Space, Spin, Table, Tag } from 'antd'
import type { TableProps } from 'antd'
import { Checkbox, List } from 'antd-mobile'
import { useState } from 'react'

import { Platform } from '@shared/platform'

import { ManageDrawer } from '../../components/ManageDrawer'
import { DATA_SCOPE_LABELS, STATUS_LABELS } from '../../constants'
import { useRoles } from '../../role/hooks/useRoles'
import type { RoleListItem } from '../../role/types'
import { getUserDetail } from '../api/userApi'
import { useUserMutations } from '../hooks/useUserMutations'
import type { UserListItem } from '../types'

interface Props {
  user: UserListItem
  onClose: () => void
}

/**
 * 用户角色管理——Drawer + 角色表格（勾选）。
 * 当前角色来自用户详情；保存只提交与初始集合的差集。
 */
export function UserRolesDrawer({ user, onClose }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user-detail', user.id],
    queryFn: () => getUserDetail(user.id),
  })
  const { data: roles = [] } = useRoles()
  const { patchRoles } = useUserMutations()

  return (
    <ManageDrawer open title={`管理角色 · ${user.username}`} onClose={onClose}>
      {isLoading ? (
        <Spin />
      ) : error ? (
        <Alert type="error" showIcon message={error.message} />
      ) : data ? (
        <UserRolesBody
          key={data.id}
          roles={roles}
          initialIds={data.roles.map((role) => role.id)}
          pending={patchRoles.isPending}
          onCancel={onClose}
          onSubmit={async (add, remove) => {
            if (!add.length && !remove.length) {
              onClose()
              return
            }
            try {
              await patchRoles.mutateAsync({
                id: user.id,
                body: { add_role_ids: add, remove_role_ids: remove },
              })
              onClose()
            } catch {
              // 错误提示由 mutation 统一处理，抽屉保留以便重试
            }
          }}
        />
      ) : null}
    </ManageDrawer>
  )
}

interface BodyProps {
  roles: RoleListItem[]
  initialIds: string[]
  pending: boolean
  onSubmit: (add: string[], remove: string[]) => void
  onCancel: () => void
}

function UserRolesBody({ roles, initialIds, pending, onSubmit, onCancel }: BodyProps) {
  const [selected, setSelected] = useState<string[]>(initialIds)
  const [keyword, setKeyword] = useState('')
  const lower = keyword.trim().toLowerCase()
  const filtered = lower
    ? roles.filter(
        (role) =>
          role.code.toLowerCase().includes(lower) || role.name.toLowerCase().includes(lower),
      )
    : roles

  const columns: TableProps<RoleListItem>['columns'] = [
    { title: '角色标识', dataIndex: 'code', width: 160 },
    { title: '名称', dataIndex: 'name' },
    {
      title: '数据范围',
      dataIndex: 'data_scope',
      width: 140,
      render: (value: RoleListItem['data_scope']) => DATA_SCOPE_LABELS[value],
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (value: RoleListItem['status']) => (
        <Tag color={value === 'active' ? 'success' : 'default'}>{STATUS_LABELS[value]}</Tag>
      ),
    },
  ]

  const handleSave = () => {
    const add = selected.filter((id) => !initialIds.includes(id))
    const remove = initialIds.filter((id) => !selected.includes(id))
    onSubmit(add, remove)
  }

  return (
    <div>
      <Input
        allowClear
        placeholder="搜索角色标识 / 名称"
        value={keyword}
        onChange={(event) => setKeyword(event.target.value)}
        style={{ marginBottom: 12 }}
      />

      <Platform
        desktop={
          <Table<RoleListItem>
            rowKey="id"
            size="small"
            columns={columns}
            dataSource={filtered}
            pagination={false}
            scroll={{ y: 420 }}
            rowSelection={{
              selectedRowKeys: selected,
              onChange: (keys) => setSelected(keys.map(String)),
            }}
          />
        }
        mobile={
          <List>
            {filtered.map((role) => (
              <List.Item
                key={role.id}
                prefix={
                  <Checkbox
                    checked={selected.includes(role.id)}
                    onChange={(checked) =>
                      setSelected((prev) =>
                        checked ? [...prev, role.id] : prev.filter((id) => id !== role.id),
                      )
                    }
                  />
                }
                description={`${role.code} · ${DATA_SCOPE_LABELS[role.data_scope]} · ${
                  STATUS_LABELS[role.status]
                }`}
              >
                {role.name}
              </List.Item>
            ))}
            {filtered.length === 0 && <List.Item>暂无匹配角色</List.Item>}
          </List>
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
        <span>已选 {selected.length} 项</span>
        <Space>
          <Button onClick={onCancel}>取消</Button>
          <Button type="primary" loading={pending} onClick={handleSave}>
            保存
          </Button>
        </Space>
      </div>
    </div>
  )
}
