import { useQuery } from '@tanstack/react-query'
import { Alert, Modal, Spin } from 'antd'

import { DeltaMultiSelectEditor } from '../../components/DeltaMultiSelectEditor'
import { useRoles } from '../../role/hooks/useRoles'
import { getUserDetail } from '../api/userApi'
import { useUserMutations } from '../hooks/useUserMutations'
import type { UserListItem } from '../types'

interface Props {
  user: UserListItem
  onClose: () => void
}

/**
 * 用户角色管理（增量）——打开时拉详情取当前角色，保存时只提交本次增删。
 * 角色选项来自角色列表（需要 `iam:role:read`，入口已按权限显隐）。
 */
export function UserRolesModal({ user, onClose }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user-detail', user.id],
    queryFn: () => getUserDetail(user.id),
  })
  const { data: roles = [] } = useRoles()
  const { patchRoles } = useUserMutations()

  const roleOptions = roles.map((role) => ({
    value: role.id,
    label: `${role.name}（${role.code}）`,
    // 停用角色不可新授予；已在集合里的仍可移除
    disabled: role.status !== 'active',
  }))

  const content = isLoading ? (
    <Spin />
  ) : error ? (
    <Alert type="error" showIcon message={error.message} />
  ) : data ? (
    <DeltaMultiSelectEditor
      key={data.id}
      initialIds={data.roles.map((role) => role.id)}
      options={roleOptions}
      placeholder="选择角色"
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
          // 错误提示由 mutation 统一处理，弹窗保留以便重试
        }
      }}
    />
  ) : null

  return (
    <Modal open title={`管理角色 · ${user.username}`} footer={null} onCancel={onClose}>
      {content}
    </Modal>
  )
}
