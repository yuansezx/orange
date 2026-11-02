import { Button, Form, Input } from 'antd'

export interface LoginFormValues {
  username: string
  password: string
}

/**
 * 登录表单（纯展示 + 校验）；提交与副作用由 `useLogin` 承担。
 * 无 label —— 用 placeholder 呈现（校验仍挂在 `name` 上，不受影响；补 `aria-label` 兼顾无障碍）。
 */
export function LoginForm({
  loading,
  onSubmit,
}: {
  loading: boolean
  onSubmit: (values: LoginFormValues) => void
}) {
  return (
    <Form<LoginFormValues>
      layout="vertical"
      size="large"
      requiredMark={false}
      onFinish={onSubmit}
    >
      <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
        <Input autoComplete="username" placeholder="用户名" aria-label="用户名" />
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
        <Input.Password
          autoComplete="current-password"
          placeholder="密码"
          aria-label="密码"
        />
      </Form.Item>
      <Form.Item style={{ marginBottom: 0 }}>
        <Button type="primary" htmlType="submit" block loading={loading}>
          登录
        </Button>
      </Form.Item>
    </Form>
  )
}
