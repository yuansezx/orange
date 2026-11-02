import { Button, Card, Typography } from 'antd'
import { useState } from 'react'

import { ChangePasswordModal } from '@features/auth'

/** 安全设置：目前先接修改密码。 */
export default function SecurityPage() {
  const [passwordOpen, setPasswordOpen] = useState(false)

  return (
    <Card title="安全设置">
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 600 }}>登录密码</div>
          <Typography.Text type="secondary">
            修改成功后所有设备将下线，需要重新登录。
          </Typography.Text>
        </div>
        <Button onClick={() => setPasswordOpen(true)}>修改密码</Button>
      </div>

      <ChangePasswordModal
        open={passwordOpen}
        onClose={() => setPasswordOpen(false)}
      />
    </Card>
  )
}
