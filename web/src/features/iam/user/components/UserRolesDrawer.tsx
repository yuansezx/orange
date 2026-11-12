import { useQuery } from '@tanstack/react-query'
import { Alert, Button, Space, Spin } from 'antd'
import { useState } from 'react'

import { ManageDrawer } from '../../components/ManageDrawer'
import { RolePicker } from '../../role/components/RolePicker'
import { getUserDetail } from '../api/userApi'
import { useUserMutations } from '../hooks/useUserMutations'
import type { UserListItem } from '../types'

interface Props {
  user: UserListItem
  onClose: () => void
}

/**
 * 用户角色管理——Drawer + 分页角色选择表（勾选）。
 * 当前角色来自用户详情；保存只提交与初始集合的差集。
 */
export function UserRolesDrawer({ user, onClose }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user-detail', user.id],
    queryFn: () => getUserDetail(user.id),
  })
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
  initialIds: string[]
  pending: boolean
  onSubmit: (add: string[], remove: string[]) => void
  onCancel: () => void
}

function UserRolesBody({ initialIds, pending, onSubmit, onCancel }: BodyProps) {
  const [selected, setSelected] = useState<string[]>(initialIds)

  const handleSave = () => {
    const add = selected.filter((id) => !initialIds.includes(id))
    const remove = initialIds.filter((id) => !selected.includes(id))
    onSubmit(add, remove)
  }

  return (
    <div>
      <RolePicker value={selected} onChange={setSelected} />

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
