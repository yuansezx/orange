import { Button, Input, Space } from 'antd'

/**
 * 【共用层】—— 两端都能用，所以放在 components/ 根目录，**不**进 desktop/、mobile/。
 *
 * 判据：这块在两端是「同一行为、不同长相」还是「不同行为」？
 *  · 同一行为（本例：搜索 + 新建）→ 留在这里共用；
 *  · 不同行为（例：桌面点「新建」弹 Modal、移动跳整页）→ 才拆到 desktop/ mobile/。
 *
 * 注意：共用组件要避免绑定某一端的重样式，否则移动端会很别扭；
 * 一旦发现"为了共用而塞一堆设备判断"，那其实就是该分叉的信号。
 */
export function UserToolbar() {
  return (
    <Space
      style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap' }}
    >
      <Input
        allowClear
        placeholder="搜索 用户名 / 昵称 / 邮箱 / 手机号"
        style={{ width: 300, maxWidth: '100%' }}
      />
      <Button type="primary">新建用户</Button>
    </Space>
  )
}
