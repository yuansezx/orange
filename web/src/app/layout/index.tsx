import { Platform } from '@shared/platform'

import { DesktopLayout } from './desktop'
import { MobileLayout } from './mobile'

/** 全局布局：按设备分叉（桌面侧边栏 / 移动端底部导航），内容区共用 <Outlet/>。 */
export function AppLayout() {
  return <Platform desktop={<DesktopLayout />} mobile={<MobileLayout />} />
}
