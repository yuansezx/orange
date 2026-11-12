import { Descriptions, Space, Tag, Typography } from 'antd'
import dayjs from 'dayjs'

import { DetailDrawer, userRefLabel } from '@shared/ui'

import { AUTH_METHOD_COLORS, AUTH_METHOD_LABELS, RESULT_LABELS } from '../constants'
import type { AuditLogItem } from '../types'

interface Props {
  open: boolean
  log: AuditLogItem | null
  onClose: () => void
}

export function AuditLogDetailDrawer({ open, log, onClose }: Props) {
  const operator = log
    ? userRefLabel(log.operator_username, log.operator_nickname) || '-'
    : '-'

  return (
    <DetailDrawer open={open} title="审计日志详情" onClose={onClose}>
      {log && (
        <Descriptions column={1} size="small" bordered>
          <Descriptions.Item label="时间">
            {dayjs(log.occurred_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          <Descriptions.Item label="动作码">{log.key}</Descriptions.Item>
          <Descriptions.Item label="摘要">{log.summary}</Descriptions.Item>
          <Descriptions.Item label="操作人">{operator}</Descriptions.Item>
          <Descriptions.Item label="来源">
            {log.auth_method ? (
              <Tag color={AUTH_METHOD_COLORS[log.auth_method]}>
                {AUTH_METHOD_LABELS[log.auth_method]}
              </Tag>
            ) : (
              '-'
            )}
          </Descriptions.Item>
          {log.api_key_id && (
            <Descriptions.Item label="API Key ID">
              <Typography.Text code>{log.api_key_id}</Typography.Text>
            </Descriptions.Item>
          )}
          <Descriptions.Item label="目标">
            <Space size={6}>
              <span>{log.target_name || log.target_id || '-'}</span>
              {log.target_type && <Tag style={{ marginInlineEnd: 0 }}>{log.target_type}</Tag>}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="结果">
            {/* solid 成功用预设绿（#52c41a）；语义 success 已被调成 filled 档的柔和色 */}
            <Tag variant="solid" color={log.result === 'success' ? 'green' : 'error'}>
              {RESULT_LABELS[log.result]}
            </Tag>
          </Descriptions.Item>
          {log.error_code && (
            <Descriptions.Item label="错误码">{log.error_code}</Descriptions.Item>
          )}
          {log.error_message && (
            <Descriptions.Item label="错误信息">{log.error_message}</Descriptions.Item>
          )}
          <Descriptions.Item label="请求 ID">{log.request_id || '-'}</Descriptions.Item>
          <Descriptions.Item label="IP">{log.ip || '-'}</Descriptions.Item>
          <Descriptions.Item label="User-Agent">{log.user_agent || '-'}</Descriptions.Item>
          <Descriptions.Item label="详情">
            <pre
              style={{
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
                fontSize: 12,
              }}
            >
              {JSON.stringify(log.detail, null, 2)}
            </pre>
          </Descriptions.Item>
        </Descriptions>
      )}
    </DetailDrawer>
  )
}
