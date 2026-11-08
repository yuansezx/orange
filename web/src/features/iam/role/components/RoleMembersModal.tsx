import { useQuery } from '@tanstack/react-query'
import { Alert, Modal, Spin } from 'antd'

import { userChoiceLabel } from '@shared/ui'

import { DeltaMultiSelectEditor } from '../../components/DeltaMultiSelectEditor'
import { getUsers } from '../../user/api/userApi'
import { getRoleUsers } from '../api/roleApi'
import { useRoleMutations } from '../hooks/useRoleMutations'
import type { RoleListItem } from '../types'

/** 用户目录一次取量（与 UserSelect 共用缓存；管理台规模小，暂不分页）。 */
const DIRECTORY_SIZE = 100

interface Props {
  role: RoleListItem
  onClose: () => void
}

/**
 * 角色成员管理（增量）——打开时拉「可管理成员」，保存时只提交本次增删。
 * 候选用户走 `GET /users`（已按数据范围过滤），需要 `iam:user:read`。
 */
export function RoleMembersModal({ role, onClose }: Props) {
  const { data: members, isLoading, error } = useQuery({
    queryKey: ['role-users', role.id],
    queryFn: () => getRoleUsers(role.id),
  })
  const { data: directory } = useQuery({
    queryKey: ['user-directory', DIRECTORY_SIZE],
    queryFn: () => getUsers({ page: 1, page_size: DIRECTORY_SIZE }),
    staleTime: 5 * 60_000,
  })
  const { patchMembers } = useRoleMutations()

  // 候选目录分页有限：把当前成员也并入选项，保证已选中的行有正确 label
  const optionMap = new Map<string, { value: string; label: string }>()
  for (const user of directory?.data ?? []) {
    optionMap.set(user.id, {
      value: user.id,
      label: userChoiceLabel(user.username, user.nickname),
    })
  }
  for (const member of members ?? []) {
    if (!optionMap.has(member.id)) {
      optionMap.set(member.id, {
        value: member.id,
        label: userChoiceLabel(member.username, member.nickname),
      })
    }
  }
  const options = [...optionMap.values()]

  const content = isLoading ? (
    <Spin />
  ) : error ? (
    <Alert type="error" showIcon message={error.message} />
  ) : members ? (
    <DeltaMultiSelectEditor
      key={role.id}
      initialIds={members.map((member) => member.id)}
      options={options}
      placeholder="选择成员"
      pending={patchMembers.isPending}
      onCancel={onClose}
      onSubmit={async (add, remove) => {
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
          // 错误提示由 mutation 统一处理，弹窗保留以便重试
        }
      }}
    />
  ) : null

  return (
    <Modal open title={`管理成员 · ${role.name}`} footer={null} onCancel={onClose}>
      {content}
    </Modal>
  )
}
