import { Platform } from '@shared/platform'

import { UserToolbar } from './components/UserToolbar'
import { UserTable } from './components/desktop/UserTable'
import { UserCardList } from './components/mobile/UserCardList'
import { useUsers } from './hooks/useUsers'

/**
 * 【平台模式范例 · 分叉档】
 *
 * 页面**只写一份**：
 *  1. 取数（useUsers）两端共用 —— 业务逻辑不感知设备；
 *  2. 工具栏（UserToolbar）两端共用 —— 同一行为、不同长相不必拆；
 *  3. 只有「列表渲染」这一处确实不同（桌面表格 / 移动卡片），才用 <Platform> 分叉。
 *
 * 要点：分叉**收口在组件边界**（下面那个 <Platform> 就是唯一的判断点），
 * 不要把设备判断散进 JSX 各处。真要整页都不同，那多半是「另一个产品」了 → 考虑另起 app。
 */
export default function UserPage() {
  const { data, isLoading, error } = useUsers({ page: 1, page_size: 10 })
  const users = data?.data ?? []

  return (
    <div>
      <UserToolbar />
      <Platform
        desktop={<UserTable users={users} loading={isLoading} error={error} />}
        mobile={<UserCardList users={users} loading={isLoading} error={error} />}
      />
    </div>
  )
}
