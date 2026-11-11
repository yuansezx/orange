import { Modal } from 'antd'

import { ApiKeyTokenView } from './ApiKeyTokenView'

interface Props {
  name: string | null
  token: string | null
  onClose: () => void
}

/** 创建成功后的明文 token 弹窗（服务端只返回一次）。 */
export function ApiKeyTokenModal({ name, token, onClose }: Props) {
  const open = name !== null && token !== null

  return (
    <Modal
      open={open}
      title="API Key（仅显示一次）"
      footer={null}
      closable={false}
      maskClosable={false}
      keyboard={false}
      destroyOnHidden
    >
      {name && token && <ApiKeyTokenView name={name} token={token} onDone={onClose} />}
    </Modal>
  )
}
