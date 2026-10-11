import type { UserListItem } from './types'

/** 占位数据：后端未就绪时供 UI 先行开发（VITE_USE_MOCK=true）。 */
export const MOCK_USERS: UserListItem[] = [
  {
    id: '01920000-0000-7000-8000-000000000001',
    username: 'admin',
    nickname: '超级管理员',
    email: 'admin@orange.dev',
    phone: null,
    user_type: 'super_admin',
    status: 'active',
    description: null,
    dept_id: null,
    created_at: '2026-10-01T08:00:00+08:00',
  },
  {
    id: '01920000-0000-7000-8000-000000000002',
    username: 'alice',
    nickname: '爱丽丝',
    email: 'alice@orange.dev',
    phone: '13800000001',
    user_type: 'admin_created',
    status: 'active',
    description: null,
    dept_id: null,
    created_at: '2026-10-02T09:30:00+08:00',
  },
]
