import { Descriptions, Tag } from 'antd'
import dayjs from 'dayjs'

import { DetailDrawer } from '@shared/ui'

import { RESULT_LABELS } from '../constants'
import type { AuditLogItem } from '../types'

interface Props {
  open: boolean
  log: AuditLogItem | null
  onClose: () => void
}

export function AuditLogDetailDrawer({ open, log, onClose }: Props) {
  const operator = log
    ? log.operator_nickname || log.operator_username || '-'
    : '-'
  const operatorAccount = log?.operator_username && log.operator_nickname
    ? ` (${log.operator_username})`
    : ''

  return (
    <DetailDrawer open={open} title="审计日志详情" onClose={onClose}>
      {log && (
        <Descriptions column={1} size="small" bordered>
          <Descriptions.Item label="时间">
            {dayjs(log.occurred_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          <Descriptions.Item label="动作码">{log.key}</Descriptions.Item>
          <Descriptions.Item label="摘要">{log.summary}</Descriptions.Item>
          <Descriptions.Item label="操作人">
            {operator}{operatorAccount}
          </Descriptions.Item>
          <Descriptions.Item label="目标">
            {log.target_name || log.target_id || '-'}
            {log.target_type ? ` (${log.target_type})` : ''}
          </Descriptions.Item>
          <Descriptions.Item label="结果">
            <Tag color={log.result === 'success' ? 'success' : 'error'}>
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
