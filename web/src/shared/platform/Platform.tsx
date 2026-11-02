import type { ReactNode } from 'react'

import { useDevice } from './useDevice'

/**
 * 平台分叉原语 —— **逃生口，按需用，不是每页都得上**。
 *
 * 只在「这一处两端行为/形态确实不同」的地方做一次选择，把分叉**收口于此**，
 * 不要把设备判断散进 JSX 各处。绝大多数页面写一份响应式实现即可（见 features/home）。
 * 用法：<Platform desktop={<A/>} mobile={<B/>} />
 */
export function Platform({ desktop, mobile }: { desktop: ReactNode; mobile: ReactNode }) {
  return <>{useDevice() === 'desktop' ? desktop : mobile}</>
}
