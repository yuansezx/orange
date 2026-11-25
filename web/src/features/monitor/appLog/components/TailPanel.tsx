import { useEffect, useRef } from 'react'

import { Alert, Button, Segmented, Space, Tag } from 'antd'

import { colorTokens } from '@shared/theme/tokens'
import { IconPlayerPlay } from '@shared/ui'

import { TAIL_FILE_OPTIONS } from '../constants'
import { useAppLogTail } from '../hooks/useAppLogTail'
import type { AppLogTailFile, AppLogTailStatus } from '../types'

const STATUS_LABELS: Record<AppLogTailStatus, string> = {
  idle: '未连接',
  connecting: '连接中',
  connected: '已连接',
  error: '已断开',
}

const STATUS_COLORS: Record<AppLogTailStatus, string> = {
  idle: 'default',
  connecting: 'processing',
  connected: 'success',
  error: 'error',
}

function placeholder(status: AppLogTailStatus): string {
  if (status === 'connecting') return '连接中…'
  if (status === 'connected') return '已连接，等待新日志…'
  if (status === 'error') return '连接已断开'
  return '点击「开始实时」查看当前日志。'
}

/** 实时日志：选择 app / error，SSE 跟随；只在贴底时自动滚动。 */
export function TailPanel() {
  const { file, setFile, lines, status, error, running, start, stop, clear } =
    useAppLogTail()
  const preRef = useRef<HTMLPreElement>(null)
  const pinnedRef = useRef(true)

  useEffect(() => {
    const el = preRef.current
    if (el && pinnedRef.current) {
      el.scrollTop = el.scrollHeight
    }
  }, [lines])

  const handleScroll = () => {
    const el = preRef.current
    if (!el) return
    pinnedRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 24
  }

  return (
    <div>
      <Space style={{ display: 'flex', marginBottom: 12 }} size={12} wrap>
        <Segmented
          value={file}
          options={TAIL_FILE_OPTIONS}
          disabled={running}
          onChange={(value) => setFile(value as AppLogTailFile)}
        />
        {running ? (
          <Button danger onClick={stop}>
            停止
          </Button>
        ) : (
          <Button
            type="primary"
            icon={<IconPlayerPlay size={16} />}
            onClick={() => {
              pinnedRef.current = true
              void start()
            }}
          >
            开始实时
          </Button>
        )}
        <Button
          onClick={() => {
            pinnedRef.current = true
            clear()
          }}
          disabled={lines.length === 0}
        >
          清空
        </Button>
        <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Tag>
      </Space>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 12 }} />}
      <pre
        ref={preRef}
        onScroll={handleScroll}
        style={{
          margin: 0,
          height: '60vh',
          overflow: 'auto',
          padding: 12,
          fontSize: 12,
          lineHeight: 1.6,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
          background: colorTokens.bgMuted,
          color: colorTokens.text,
          border: `1px solid ${colorTokens.border}`,
          borderRadius: 8,
        }}
      >
        {lines.length > 0 ? lines.join('\n') : placeholder(status)}
      </pre>
    </div>
  )
}
