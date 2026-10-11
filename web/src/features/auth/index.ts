/**
 * 认证切片（控制台级）——**门面**。
 *
 * 说明：本切片不贡献应用壳内的路由/导航（登录页在壳**之外**），故不进 `app/routes.ts`
 * 的 `features` 注册表；改由 `app/router.tsx` 直接引用（`/login` + `RequireAuth`）。
 */
export { LoginPage } from './LoginPage'
export { RequireAuth } from './RequireAuth'
export { useLogin } from './hooks/useLogin'
export { useMe } from './hooks/useMe'
export type { CurrentUser, LoginReq, LoginResp, RoleSummary, UserType } from './types'
