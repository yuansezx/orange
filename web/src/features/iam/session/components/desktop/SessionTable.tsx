import { Alert, Button, Table, theme, Tooltip, Typography } from 'antd'
import type { TableProps } from 'antd'
import { useMemo, useState } from 'react'
import type { Key } from 'react'

import { IconLogout, IconUserX } from '@shared/ui'

import { browserText, formatTime, osText, userLabel } from '../../sessionFormat'
import type { SessionListViewProps, SessionTableRow } from '../../types'

interface Props extends SessionListViewProps {
  onSelectionChange: (keys: string[]) => void
}

/**
 * 【分叉档 · 桌面】按用户分组、可展开的会话表格。
 * 勾选用户行 = 踢其全部会话；勾选会话行 = 踢指定会话（`checkStrictly`，父子不联动）。
 */
export function SessionTable({
  groups,
  loading,
  error,
  canRevokeSessions,
  canRevokeUsers,
  selectedKeys,
  onSelectionChange,
  onRevokeUser,
  onRevokeSession,
}: Props) {
  const { token } = theme.useToken()
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set())

  const groupKeys = useMemo(() => groups.map((group) => group.key), [groups])
  // 异步数据下 defaultExpandAllRows 不生效：展开态 = 全部用户行 - 被折叠的行
  const expandedRowKeys = groupKeys.filter((key) => !collapsed.has(key))

  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const columns: TableProps<SessionTableRow>['columns'] = [
    {
      title: '用户 / 浏览器',
      key: 'who',
      ellipsis: true,
      render: (_, record) =>
        record.kind === 'user' ? (
          <span>
            <strong>{userLabel(record)}</strong>
            {record.username && (
              <Typography.Text type="secondary"> @{record.username}</Typography.Text>
            )}
          </span>
        ) : (
          browserText(record)
        ),
    },
    {
      title: '系统 / 设备',
      key: 'os',
      width: 220,
      render: (_, record) =>
        record.kind === 'user' ? `${record.session_count} 个会话` : osText(record),
    },
    {
      title: '登录 IP',
      key: 'ip',
      width: 150,
      render: (_, record) => (record.kind === 'session' ? record.login_ip || '-' : '-'),
    },
    {
      title: '登录时间',
      key: 'login_at',
      width: 180,
      render: (_, record) => (record.kind === 'session' ? formatTime(record.login_at) : '-'),
    },
    {
      title: '过期时间',
      key: 'expires_at',
      width: 180,
      render: (_, record) => (record.kind === 'session' ? formatTime(record.expires_at) : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 90,
      render: (_, record) =>
        record.kind === 'user'
          ? canRevokeUsers && (
              <Tooltip title="踢出该用户全部会话">
                <Button
                  type="text"
                  danger
                  icon={<IconUserX size={16} />}
                  onClick={() => onRevokeUser(record)}
                />
              </Tooltip>
            )
          : canRevokeSessions && (
              <Tooltip title="踢下线">
                <Button
                  type="text"
                  danger
                  icon={<IconLogout size={16} />}
                  onClick={() => onRevokeSession(record)}
                />
              </Tooltip>
            ),
    },
  ]

  return (
    <Table<SessionTableRow>
      rowKey="key"
      loading={loading}
      columns={columns}
      dataSource={groups}
      pagination={false}
      rowSelection={
        canRevokeSessions || canRevokeUsers
          ? {
              selectedRowKeys: [...selectedKeys],
              checkStrictly: true,
              onChange: (keys: Key[]) => onSelectionChange(keys.map(String)),
              getCheckboxProps: (record) => ({
                disabled: record.kind === 'session' ? !canRevokeSessions : !canRevokeUsers,
              }),
            }
          : undefined
      }
      onRow={(record) => ({
        style: record.kind === 'user' ? { background: token.colorFillAlter } : undefined,
      })}
      expandable={{
        expandedRowKeys,
        onExpandedRowsChange: (keys) => {
          const expanded = new Set(keys.map(String))
          setCollapsed(new Set(groupKeys.filter((key) => !expanded.has(key))))
        },
      }}
    />
  )
}
