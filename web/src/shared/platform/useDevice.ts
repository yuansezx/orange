import { useSyncExternalStore } from 'react'

import { BREAKPOINTS, type DeviceType } from './breakpoints'

const QUERY = `(min-width: ${BREAKPOINTS.desktop}px)`

function subscribe(onChange: () => void): () => void {
  const mql = window.matchMedia(QUERY)
  mql.addEventListener('change', onChange)
  return () => mql.removeEventListener('change', onChange)
}

function getSnapshot(): DeviceType {
  return window.matchMedia(QUERY).matches ? 'desktop' : 'mobile'
}

/**
 * 设备类型（按视口宽度，非 UA 嗅探）——响应式、可随窗口缩放实时切换。
 * 视图分叉统一走它，业务逻辑不感知设备。
 */
export function useDevice(): DeviceType {
  return useSyncExternalStore(subscribe, getSnapshot)
}
