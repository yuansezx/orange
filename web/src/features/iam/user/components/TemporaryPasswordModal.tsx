import { Modal } from 'antd'

import { TemporaryPasswordView } from './TemporaryPasswordView'

interface Props {
  username: string | null
  password: string | null
  onClose: () => void
}

/** 创建用户后的临时密码弹窗（服务端只在生成时回传一次）。 */
export function TemporaryPasswordModal({ username, password, onClose }: Props) {
  const open = username !== null && password !== null

  return (
    <Modal
      open={open}
      title="临时密码（仅显示一次）"
      footer={null}
      closable={false}
      maskClosable={false}
      keyboard={false}
      destroyOnHidden
    >
      {username && password && (
        <TemporaryPasswordView username={username} password={password} onDone={onClose} />
      )}
    </Modal>
  )
}
