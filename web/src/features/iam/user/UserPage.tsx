import { App } from 'antd'
import { useSearchParams } from 'react-router-dom'

import { Platform } from '@shared/platform'

import { UserToolbar } from './components/UserToolbar'
import { UserTable } from './components/desktop/UserTable'
import { UserCardList } from './components/mobile/UserCardList'
import { useUsers } from './hooks/useUsers'
import type { GetUsersQuery, UserStatus, UserType } from './types'

/**
 * 【平台模式范例 · 分叉档】
 *
 * 页面**只写一份**：
 *  1. 取数（useUsers）两端共用 —— 业务逻辑不感知设备；
 *  2. 工具栏（UserToolbar）两端共用；
 *  3. 只有「列表渲染」确实不同（桌面表格 / 移动卡片），才用 <Platform> 分叉。
 *
 * 筛选/分页状态放 **URL query**（可分享、刷新不丢）；改动即触发 TanStack Query 重新取数。
 */
export default function UserPage() {
  const [params, setParams] = useSearchParams()
  const { message } = App.useApp()

  const page = Number(params.get('page') ?? '1') || 1
  const pageSize = Number(params.get('page_size') ?? '10') || 10
  const keyword = params.get('keyword') ?? ''
  const status = (params.get('status') as UserStatus | null) ?? undefined
  const userType = (params.get('user_type') as UserType | null) ?? undefined

  const query: GetUsersQuery = {
    page,
    page_size: pageSize,
    keyword: keyword || undefined,
    status,
    user_type: userType,
  }
  const { data, isLoading, error } = useUsers(query)
  const users = data?.data ?? []

  /** 改筛选/分页：patch 的键即 URL query 参数名；不带 page 的改动回到第 1 页。 */
  const update = (patch: Record<string, string | undefined>) => {
    const next = new URLSearchParams(params)
    for (const [key, value] of Object.entries(patch)) {
      if (value) next.set(key, value)
      else next.delete(key)
    }
    if (!('page' in patch)) next.set('page', '1')
    setParams(next, { replace: true })
  }

  return (
    <div>
      <UserToolbar
        keyword={keyword}
        status={status}
        userType={userType}
        onChange={update}
        onCreate={() => message.info('创建用户：待实现')}
      />
      <Platform
        desktop={
          <UserTable
            users={users}
            loading={isLoading}
            error={error}
            total={data?.total ?? 0}
            page={page}
            pageSize={pageSize}
            onPageChange={(nextPage, nextSize) =>
              update({ page: String(nextPage), page_size: String(nextSize) })
            }
          />
        }
        mobile={<UserCardList users={users} loading={isLoading} error={error} />}
      />
    </div>
  )
}
