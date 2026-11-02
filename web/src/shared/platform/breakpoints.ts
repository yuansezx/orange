/** 平台分叉的断点与设备类型。 */
export const BREAKPOINTS = {
  /** ≥ 该宽度视为桌面端。 */
  desktop: 768,
} as const

export type DeviceType = 'desktop' | 'mobile'
