import { Tabs } from 'antd'

import { ArchivedLogsPanel } from './components/ArchivedLogsPanel'
import { TailPanel } from './components/TailPanel'

/** 应用日志：归档文件（查看 / 下载 / 手动归档）+ 实时 tail。 */
export default function AppLogPage() {
  return (
    <Tabs
      defaultActiveKey="archived"
      items={[
        { key: 'archived', label: '归档日志', children: <ArchivedLogsPanel /> },
        { key: 'tail', label: '实时日志', children: <TailPanel /> },
      ]}
    />
  )
}
