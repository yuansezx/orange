import { Dropdown } from 'antd'

import { UserAvatar } from '@shared/ui'

import { useLogout } from '../hooks/useLogout'
import { useMe } from '../hooks/useMe'

/**
 * 用户区（头像 + 昵称 → 下拉菜单）——桌面壳与导航页共用。
 * 菜单项目前只有「退出登录」；有「修改密码 / 个人资料」页后再往里加。
 */
export function UserMenu() {
  const { data: me } = useMe()
  const { logout } = useLogout()

  if (!me) return null

  return (
    <Dropdown
      trigger={['click']}
      placement="bottomRight"
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
          gap: 8,
          maxWidth: 180,
          cursor: 'pointer',
        }}
      >
        <UserAvatar name={me.nickname} src={me.avatar} size={28} />
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {me.nickname}
        </span>
      </div>
    </Dropdown>
  )
}
