import { Alert, App, Button, Card, Empty, Table, Tag, Typography } from 'antd'
import { Button as MobileButton, List as MobileList } from 'antd-mobile'
import type { TableProps } from 'antd'

import { Platform } from '@shared/platform'
import { IconDevices, IconLogout } from '@shared/ui'

import { browserText, formatTime, osText } from '../session/sessionFormat'
import { useMySessions, useRevokeMySessions } from './hooks/useMySessions'
import type { MySession } from './types'

/** 自助在线设备：只展示本人会话，标记当前设备；支持退出单个 / 其他设备。 */
export default function SessionsPage() {
  const { data, isLoading, error } = useMySessions()
  const revoke = useRevokeMySessions()
  const { modal } = App.useApp()

  const sessions = data ?? []
  const others = sessions.filter((session) => !session.is_current)

  const confirmRevoke = (targets: MySession[]) => {
    if (!targets.length) return
    modal.confirm({
      title: targets.length === 1 ? '退出该设备？' : `退出 ${targets.length} 台设备？`,
      content: '这些设备需要重新登录才能继续使用。',
      okText: '退出',
      okButtonProps: { danger: true },
      onOk: () => revoke.mutateAsync(targets.map((session) => session.session_id)),
    })
  }

  const title = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
      <span style={{ flex: 1, minWidth: 0 }}>在线设备</span>
      <Button
        danger
        icon={<IconLogout size={16} />}
        disabled={!others.length}
        loading={revoke.isPending}
        onClick={() => confirmRevoke(others)}
      >
        退出其他设备
      </Button>
    </div>
  )

  const columns: TableProps<MySession>['columns'] = [
    {
      title: '设备 / 浏览器',
      key: 'browser',
      render: (_, session) => (
        <span>
          {browserText(session)}
          {session.is_current && (
            <Tag color="success" style={{ marginInlineStart: 8 }}>
              当前设备
            </Tag>
          )}
        </span>
      ),
    },
    {
      title: '系统 / 设备',
      key: 'os',
      width: 220,
      render: (_, session) => osText(session),
    },
    {
      title: '登录 IP',
      dataIndex: 'login_ip',
      width: 150,
      render: (value: string | null) => value || '-',
    },
    {
      title: '登录时间',
      dataIndex: 'login_at',
      width: 180,
      render: (value: string) => formatTime(value),
    },
    {
      title: '过期时间',
      dataIndex: 'expires_at',
      width: 180,
      render: (value: string) => formatTime(value),
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_, session) =>
        session.is_current ? (
          <Typography.Text type="secondary">当前</Typography.Text>
        ) : (
          <Button
            type="text"
            danger
            icon={<IconLogout size={16} />}
            onClick={() => confirmRevoke([session])}
          />
        ),
    },
  ]

  const desktop = (
    <Table<MySession>
      rowKey="session_id"
      columns={columns}
      dataSource={sessions}
      pagination={false}
    />
  )

  const mobile = (
    <>
      <Typography.Text type="secondary">
        {others.length ? `当前设备之外还有 ${others.length} 台设备在线` : '没有其他在线设备'}
      </Typography.Text>
      <MobileList style={{ marginTop: 8 }}>
        {sessions.map((session) => (
          <MobileList.Item
            key={session.session_id}
            prefix={<IconDevices size={20} />}
            description={
              <div>
                <div>{osText(session)}</div>
                <div>
                  {session.login_ip || '未知 IP'} · 登录 {formatTime(session.login_at)}
                </div>
                <div>过期 {formatTime(session.expires_at)}</div>
              </div>
            }
            extra={
              session.is_current ? (
                <Tag color="success">当前</Tag>
              ) : (
                <MobileButton
                  size="mini"
                  color="danger"
                  fill="none"
                  onClick={() => confirmRevoke([session])}
                >
                  退出
                </MobileButton>
              )
            }
          >
            {browserText(session)}
          </MobileList.Item>
        ))}
      </MobileList>
    </>
  )

  return (
    <Card title={title} loading={isLoading}>
      {error ? (
        <Alert type="error" message={error.message} showIcon />
      ) : sessions.length === 0 ? (
        <Empty description="暂无在线设备" />
      ) : (
        <Platform desktop={desktop} mobile={mobile} />
      )}
    </Card>
  )
}
