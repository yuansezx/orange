import { QueryClientProvider } from '@tanstack/react-query'
import { App as AntdApp, ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import type { ReactNode } from 'react'
import { BrowserRouter } from 'react-router-dom'

import { queryClient } from '@shared/query'

import { antdTheme } from './theme'

/**
 * 组合根的 Provider 装配：主题 / 服务器状态 / 路由。
 * `AntdApp` 提供带上下文的 message / notification / modal（`App.useApp()` 取用），
 * 避免用 antd 的静态方法（拿不到 ConfigProvider 主题、且 v6 已不推荐）。
 * `modal={{ centered: true }}`：确认框统一垂直居中（antd 默认偏上）。
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <ConfigProvider locale={zhCN} theme={antdTheme} modal={{ centered: true }}>
      <AntdApp>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>{children}</BrowserRouter>
        </QueryClientProvider>
      </AntdApp>
    </ConfigProvider>
  )
}
