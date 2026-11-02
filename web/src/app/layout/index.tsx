import { Platform } from '@shared/platform'

import { DesktopAdminShell } from './desktop'
import { MobileAdminShell } from './mobile'

/**
 * 系统壳：只负责 workspace 切换（左 rail）+ 用户；内容区交给 workspace 自己排版。
 * 系统级右栏当前预留但隐藏；详情右栏由 workspace 壳提供。
 */
export function AppShell() {
  return (
    <Platform desktop={<DesktopAdminShell />} mobile={<MobileAdminShell />} />
  )
}
