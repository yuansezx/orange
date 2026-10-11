import { Card, Typography } from 'antd'

/**
 * 【平台模式范例 · 共用档】
 *
 * 本页两端差异很小，**一份响应式实现**即可，故不拆 desktop/mobile。
 * 简单 feature 连 components/ 都不需要，页面直接写在这一层。
 *
 * 对照「确实分叉」的做法见 features/user（列表渲染处用了 <Platform>）。
 * 判据：同一行为、不同长相 → 共用（本页）；不同行为 → 才下沉分叉。
 */
export default function HomePage() {
  return (
    <Card>
      <Typography.Title level={4} style={{ marginTop: 0 }}>
        概览
      </Typography.Title>
      <Typography.Paragraph type="secondary" style={{ marginBottom: 0 }}>
        骨架已就绪：组合根（app）+ 共享内核（shared）+ 业务模块（features）+ 平台分叉。
        本页两端共用一份实现；分叉范例见「用户」页。
      </Typography.Paragraph>
    </Card>
  )
}
