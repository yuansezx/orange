import { useCallback, useEffect, useRef, useState } from 'react'

import { emitSessionExpired } from '@shared/auth/session'
import { getToken, setToken } from '@shared/auth/token'

import type { AppLogTailFile, AppLogTailStatus } from '../types'

const MAX_LINES = 2000

/**
 * 实时日志（SSE）：用 fetch + ReadableStream 读取，才能带 Bearer 头。
 * 只保留最近 MAX_LINES 行；停止 = abort 请求。
 */
export function useAppLogTail() {
  const [file, setFileState] = useState<AppLogTailFile>('app')
  const [lines, setLines] = useState<string[]>([])
  const [status, setStatus] = useState<AppLogTailStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const controllerRef = useRef<AbortController | null>(null)

  const append = useCallback((line: string) => {
    setLines((prev) => [...prev.slice(-(MAX_LINES - 1)), line])
  }, [])

  const stop = useCallback(() => {
    controllerRef.current?.abort()
    controllerRef.current = null
    setStatus('idle')
  }, [])

  const clear = useCallback(() => setLines([]), [])

  const setFile = useCallback((next: AppLogTailFile) => {
    setFileState(next)
  }, [])

  const start = useCallback(async () => {
    stop()
    setLines([])
    setError(null)
    setStatus('connecting')

    const controller = new AbortController()
    controllerRef.current = controller
    const token = getToken()

    try {
      const resp = await fetch(`/api/monitor/app-logs/tail?file=${file}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        signal: controller.signal,
        cache: 'no-store',
      })
      if (!resp.ok || !resp.body) {
        if (resp.status === 401) {
          setToken(null)
          emitSessionExpired()
        }
        throw new Error(await _errorMessage(resp))
      }
      setStatus('connected')
      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        let index: number
        while ((index = buffer.indexOf('\n\n')) >= 0) {
          const chunk = buffer.slice(0, index)
          buffer = buffer.slice(index + 2)
          _handleChunk(chunk, append)
        }
      }
      if (controllerRef.current === controller) {
        setStatus('idle')
      }
    } catch (err) {
      if (controller.signal.aborted) return
      setStatus('error')
      setError(err instanceof Error ? err.message : '实时日志连接失败')
    }
  }, [append, file, stop])

  useEffect(() => () => controllerRef.current?.abort(), [])

  const running = status === 'connecting' || status === 'connected'
  return {
    file,
    setFile,
    lines,
    status,
    error,
    running,
    start,
    stop,
    clear,
  }
}

async function _errorMessage(resp: Response): Promise<string> {
  const text = await resp.text()
  try {
    const body = JSON.parse(text) as { message?: string }
    if (body.message) return body.message
  } catch {
    // 非 JSON，回退到状态码
  }
  return `连接失败（${resp.status}）`
}

function _handleChunk(
  chunk: string,
  append: (line: string) => void,
): void {
  let event = 'message'
  const dataLines: string[] = []
  for (const raw of chunk.split('\n')) {
    if (raw.startsWith(':')) continue
    if (raw.startsWith('event:')) {
      event = raw.slice('event:'.length).trim()
      continue
    }
    if (raw.startsWith('data:')) {
      dataLines.push(raw.slice('data:'.length).replace(/^ /, ''))
    }
  }
  if (dataLines.length === 0) return
  const text = dataLines.join('\n')
  append(event === 'rotated' ? `--- ${text} ---` : text)
}
