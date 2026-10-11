import { Platform } from '@shared/platform'

import { DesktopAdminShell } from './desktop'
import { MobileAdminShell } from './mobile'

/** 应用壳（后台管理）——按设备分叉：桌面侧栏 / 移动抽屉。 */
export function AdminShell() {
  return <Platform desktop={<DesktopAdminShell />} mobile={<MobileAdminShell />} />
}
