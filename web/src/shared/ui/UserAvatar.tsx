import { Avatar } from 'antd'

/** 用户头像：有图用图，否则回退到**昵称首字**（同 Microsoft 的做法）。 */
export function UserAvatar({
  name,
  src,
  size = 28,
}: {
  name: string
  src?: string | null
  size?: number
}) {
  const initial = name.trim().charAt(0).toUpperCase() || '?'
  return (
    <Avatar size={size} src={src || undefined}>
      {src ? null : initial}
    </Avatar>
  )
}
