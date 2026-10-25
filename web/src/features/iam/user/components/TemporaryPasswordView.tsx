import { Button, Descriptions, Typography } from 'antd'
import { useEffect, useState } from 'react'

const ACK_DELAY_MS = 1000

interface Props {
  username: string
  password: string
  onDone: () => void
}

/** 一次性临时密码展示：用户名 + 密码，确认按钮延迟 1 秒可点（防手滑关闭）。 */
export function TemporaryPasswordView({ username, password, onDone }: Props) {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setReady(true), ACK_DELAY_MS)
    return () => window.clearTimeout(timer)
  }, [])

  return (
    <div>
      <p>请立即复制并妥善告知该用户，关闭后无法再次查看。</p>
      <Descriptions column={1} size="small" bordered>
        <Descriptions.Item label="用户名">{username}</Descriptions.Item>
        <Descriptions.Item label="临时密码">
          <Typography.Text copyable>{password}</Typography.Text>
        </Descriptions.Item>
      </Descriptions>
      <div style={{ textAlign: 'right', marginTop: 16 }}>
        <Button type="primary" disabled={!ready} onClick={onDone}>
          知道了
        </Button>
      </div>
    </div>
  )
}
