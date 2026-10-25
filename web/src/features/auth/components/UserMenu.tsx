import { Dropdown } from 'antd'

import { UserAvatar } from '@shared/ui'

import { useLogout } from '../hooks/useLogout'
import { useMe } from '../hooks/useMe'

/**
 * 用户区（头像 + 昵称 → 下拉菜单）——桌面壳与导航页共用。
 * 菜单项目前只有「退出登录」；有「修改密码 / 个人资料」页后再往里加。
 */
interface Props {
  /** 弹出方向；侧边栏底部用 `topLeft`，顶栏用默认 `bottomRight`。 */
  placement?: 'bottomRight' | 'topLeft' | 'top'
  /** 侧栏折叠轨道：只显示头像。 */
  compact?: boolean
}

export function UserMenu({ placement = 'bottomRight', compact = false }: Props) {
  const { data: me } = useMe()
  const { logout } = useLogout()

  if (!me) return null

  return (
    <Dropdown
      trigger={['click']}
      placement={placement}
      menu={{
        items: [{ key: 'logout', label: '退出登录', danger: true }],
        onClick: ({ key }) => {
          if (key === 'logout') logout()
        },
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: compact ? 'center' : undefined,
          gap: compact ? 0 : 8,
          width: compact ? '100%' : undefined,
          maxWidth: compact ? undefined : 180,
          cursor: 'pointer',
        }}
      >
        <UserAvatar name={me.nickname} src={me.avatar} size={28} />
        {!compact && (
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {me.nickname}
          </span>
        )}
      </div>
    </Dropdown>
  )
}
