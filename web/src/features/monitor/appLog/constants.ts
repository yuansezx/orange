import type { AppLogTailFile } from './types'

export const TAIL_FILE_OPTIONS: { label: string; value: AppLogTailFile }[] = [
  { label: 'app.log', value: 'app' },
  { label: 'error.log', value: 'error' },
]

export function formatBytes(size: number): string {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  return `${(size / 1024 / 1024 / 1024).toFixed(1)} GB`
}
