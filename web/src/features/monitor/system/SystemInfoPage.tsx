import { useMemo } from 'react'
import { Alert, Button, Card, Descriptions, Space, Table, Typography } from 'antd'

import { appConfig } from '@shared/config'
import { IconRefresh } from '@shared/ui'

import { useSystemVersions } from './hooks/useSystemVersions'
import { frontendModuleVersions } from './moduleVersions'
import type { ModuleVersionRow } from './types'

/** 版本信息：平台前后端 + 非平台模块前后端。 */
export default function SystemInfoPage() {
  const { data, isFetching, error, refetch } = useSystemVersions()

  const rows = useMemo<ModuleVersionRow[]>(() => {
    const merged = new Map<string, ModuleVersionRow>()
    for (const item of data?.modules ?? []) {
      merged.set(item.name, {
        name: item.name,
        backend_version: item.version,
        frontend_version: null,
      })
    }
    for (const [name, version] of Object.entries(frontendModuleVersions)) {
      const row = merged.get(name)
      if (row) {
        row.frontend_version = version
      } else {
        merged.set(name, { name, backend_version: null, frontend_version: version })
      }
    }
    return [...merged.values()].sort((a, b) => a.name.localeCompare(b.name))
  }, [data])

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      {error && (
        <Alert type="error" showIcon message="版本信息加载失败" description={error.message} />
      )}
      <Card
        title="平台"
        extra={(
          <Button
            size="small"
            icon={<IconRefresh size={16} />}
            loading={isFetching}
            onClick={() => refetch()}
          >
            刷新
          </Button>
        )}
      >
        <Descriptions
          column={{ xs: 1, sm: 1, md: 3 }}
          items={[
            { key: 'name', label: '应用', children: appConfig.name },
            { key: 'backend', label: '后端版本', children: data?.platform_version ?? '—' },
            { key: 'frontend', label: '前端版本', children: appConfig.version },
          ]}
        />
      </Card>
      <Card title="非平台模块">
        <Table<ModuleVersionRow>
          rowKey="name"
          size="small"
          loading={isFetching && !data}
          dataSource={rows}
          pagination={false}
          scroll={{ x: 480 }}
          columns={[
            { title: '模块', dataIndex: 'name' },
            {
              title: '后端版本',
              dataIndex: 'backend_version',
              render: (value: string | null) => value ?? '—',
            },
            {
              title: '前端版本',
              dataIndex: 'frontend_version',
              render: (value: string | null) => value ?? '—',
            },
          ]}
        />
        <Typography.Text type="secondary">
          后端版本来自模块 pyproject.toml，前端版本来自模块 package.json。
        </Typography.Text>
      </Card>
    </Space>
  )
}
