import { Button, Descriptions, Typography } from 'antd'
import { useEffect, useState } from 'react'

const ACK_DELAY_MS = 1000

interface Props {
  name: string
  token: string
  onDone: () => void
}

/** 一次性 API Key 展示：名称 + 明文 token，确认按钮延迟 1 秒可点（防手滑关闭）。 */
export function ApiKeyTokenView({ name, token, onDone }: Props) {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setReady(true), ACK_DELAY_MS)
    return () => window.clearTimeout(timer)
  }, [])

  return (
    <div>
      <p>请立即复制并妥善保管，关闭后无法再次查看。</p>
      <Descriptions column={1} size="small" bordered>
        <Descriptions.Item label="名称">{name}</Descriptions.Item>
        <Descriptions.Item label="API Key">
          <Typography.Text copyable code>
            {token}
          </Typography.Text>
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
