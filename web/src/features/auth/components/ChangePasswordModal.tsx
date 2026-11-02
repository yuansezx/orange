import { Form, Input, Modal } from 'antd'

import { useChangePassword } from '../hooks/useChangePassword'
import type { ChangePasswordReq } from '../types'

interface FormValues extends ChangePasswordReq {
  confirm_password: string
}

interface Props {
  open: boolean
  onClose: () => void
}

/** 自助改密弹窗：成功后服务端吊销全部会话，由用例回登录页。 */
export function ChangePasswordModal({ open, onClose }: Props) {
  const [form] = Form.useForm<FormValues>()
  const { submit, loading } = useChangePassword()

  const close = () => {
    form.resetFields()
    onClose()
  }

  return (
    <Modal
      open={open}
      title="修改密码"
      okText="确认修改"
      cancelText="取消"
      confirmLoading={loading}
      onOk={() => form.submit()}
      onCancel={close}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        requiredMark={false}
        onFinish={(values) =>
          submit(
            { old_password: values.old_password, new_password: values.new_password },
            { onSuccess: close },
          )
        }
      >
        <Form.Item
          name="old_password"
          label="当前密码"
          rules={[{ required: true, message: '请输入当前密码' }]}
        >
          <Input.Password autoComplete="current-password" />
        </Form.Item>
        <Form.Item
          name="new_password"
          label="新密码"
          rules={[
            { required: true, message: '请输入新密码' },
            {
              validator: (_, value: string | undefined) =>
                !value || value.length >= 8
                  ? Promise.resolve()
                  : Promise.reject(new Error('密码长度不能少于 8 位')),
            },
          ]}
        >
          <Input.Password autoComplete="new-password" />
        </Form.Item>
        <Form.Item
          name="confirm_password"
          label="确认新密码"
          dependencies={['new_password']}
          rules={[
            { required: true, message: '请再次输入新密码' },
            ({ getFieldValue }) => ({
              validator: (_, value: string | undefined) =>
                !value || getFieldValue('new_password') === value
                  ? Promise.resolve()
                  : Promise.reject(new Error('两次输入的新密码不一致')),
            }),
          ]}
        >
          <Input.Password autoComplete="new-password" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
