# Orange 前端（web）指南

管理台前端：**登录页 → 系统壳（workspace 栏）→ workspace 内容（模块内自管布局）**；个人中心为系统级 `/account`。
与后端同仓（后端在 `app/`，见根 `CLAUDE.md`）；前后端同仓、单 git 仓。

## 技术栈

- Vite + React 19 + TypeScript；包管理 `pnpm`
- 路由 `react-router-dom` v7
- **服务器状态** TanStack Query v5；**客户端状态** zustand
- UI：`antd`（桌面）+ `antd-mobile`（移动）
- HTTP `axios`；表单用 **antd `Form`**（依赖里的 `react-hook-form` / `zod` 未使用）
- 图标：**Tabler**（`@tabler/icons-react`）——**收口在 `shared/ui/icons.ts`**（按需再导出），别在页面直接引库；颜色随 `currentColor` 走主题

## 目录结构

```
web/src/
├── app/        # 组合根（= 后端 app 工厂）：providers / router / routes / layout
├── shared/     # 共享内核（= 后端 core，无业务语义）：api / platform / query / ui / config / auth / navigation / shell / theme
└── features/   # 切片，两类：
    ├── <模块>/           # ① 模块型：对齐后端模块（iam / monitor…）
    │   ├── <页面>/       #    每个页面：api / hooks / components / types.ts
    │   ├── components/   #    模块内共用件（如部门选择器）——留模块内，别上浮到 shared
    │   └── index.ts      #    门面：导出 FeatureModule（见下「导航/菜单」）
    └── <控制台级>/       # ② 控制台级：不属任何后端模块（auth 登录）
        └── index.ts
```

## 约定

- **依赖单向**：`app → features → shared`。feature 不认识 app；跨 feature 只能经其**门面** `@features/<name>`，**禁止深入内部路径**——由 ESLint `no-restricted-imports` 强守（见 `eslint.config.js`）。
- **模块自报门面**：模块型 feature 在 `index.ts` 导出名为 `feature` 的 `FeatureModule`（`groups`: 菜单分组；**每个菜单项同时承载它的路由** `{key,label,path,permission?,element}`——菜单与路由一处声明，杜绝"菜单指向不存在的页"）。组合根 `app/routes.ts` 用 **`import.meta.glob` 构建期发现** `features/*/index.ts`（有就加载、没有就跳过，新增模块免登记；控制台级切片不导出 `feature` 即自动排除）。**不做前端模块配置**：可见性由后端权限码过滤菜单承担，避免与后端 `core.modules` 形成第二份清单。
- **导航 / 菜单（菜单归前端）**：后端只发**权限**（`/me` 的 `permission_codes` + `user_type`），**菜单由前端声明**、按 `usePermission().can(code)` 过滤（**超管 `user_type=super_admin` 旁路**）。层次：
  - **系统壳 `AppShell`**：左侧只放用户视角的 **Workspace**（后台管理、音乐……）+ 用户区；支持 `hidden/rail/expanded` 三态和 `push/overlay`（后台管理 `push`）。形态状态只在内存，不做持久化。
  - **Workspace 壳**（`WorkspaceLayout`）：在系统内容区里自管左中右；后台管理的左侧是内部 Feature 菜单，右侧是**非模态详情右栏**（不锁背景）。
  - **FeatureModule**：对齐后端模块（iam/monitor…），声明 `workspace`、`groups`（workspace 内菜单）和可选 `settings`（个人中心设置）。完整路由为 `{workspace.basePath}/{feature}/{path}`（如 `/admin/iam/users`）；没有导航页，`/` 按权限落到第一个可访问页面。
  - **个人中心**：系统级 `/account`，设置菜单由各 feature 的 `settings` 聚合，路径 `/account/{feature}/{path}`。
  - 菜单项不带 `permission` = 永远可见；过滤只是 UX，后端 403 兜底。
- **features 对齐后端模块**：模块型切片与后端模块**同名同边界**（`iam` / `monitor`…），**不按"iam 的某张表"平铺**（否则 iam 专属的共享件无处安放）；控制台级切片（`auth`）例外。例：`features/iam/user`。
- **平台分叉**：**默认一份响应式实现**；`shared/platform` 的 `<Platform desktop={} mobile={}/>` 是**逃生口、按需用**。判据：同一行为、不同长相 → 共用；不同行为 → 才拆。跨端**共用**组件放 `components/` **根目录**，只有**确实分叉**的才进 `components/desktop/` `mobile/`；取数等逻辑放页面层共用、视图只渲染。范例：`features/iam/user`（一处叶子分叉）；系统壳本身也是分叉——桌面 = 系统 workspace 栏（三态）+ 内容（workspace 自管左中右），移动 = 顶栏（汉堡）+ workspace 抽屉 + 内容；个人中心暂用顶部设置选择器。
- **服务器状态**用 TanStack Query；`shared/api` 只出 `get/post/put/del<T>`，错误统一归一为 `ApiError`（`code` 对齐后端错误体，可 `except`/按 `code` 区分）。
- **配置**：值是**数据**，放 `src/config.json`；读取层 `shared/config/index.ts` 只"读数据 + 定型"，不含配置值。`appVersion` 构建期从 `package.json` 注入（`__APP_VERSION__`），dev 未注入时 `typeof` 兜底 `'dev'`。
- **配色收敛**：颜色一律走 **`@shared/theme/tokens`**（**唯一来源**），组件里**别写死 hex**；antd 主题 `app/theme.ts` 也引同一份 token。**多套方案**放在 `colorSchemes`，**当前生效**的由 `config.json` 的 `colorScheme` 选定（改值 → 重新构建，构建期非运行时）；消费方一律引 `colorTokens`。之所以自建而非用 antd 的 CSS 变量：本项目同时用 antd 与 antd-mobile（两套主题系统），需要两家之上的共同来源才能收敛到一处。
- 别名：`@app` / `@shared` / `@features` / `@`（见 `vite.config.ts` 与 `tsconfig.app.json`）。

## 对接后端

- dev 走 vite **proxy**：`/api` → `http://127.0.0.1:41000`（后端不做 CORS，部署走 nginx）。
- 路由前缀 `/api/{module}`（iam 即 `/api/iam`，如 `/api/iam/auth/login`、`/api/iam/users`）；`Authorization: Bearer` 认证。
- iam 列表/详情响应带审计（生命周期时间 + 操作人快照）；回收站视图用 `?deleted=true`；启用/停用走统一 `PUT /{resource}/{id}/status`。
- 错误体统一 `{code, message, details}`（成功侧不套信封）。
- **401 与会话失效**：拦截器（`shared/api/client.ts`）按后端 `code` 区分——`IAM_AUTHENTICATION_FAILED`（登录凭据错，留给表单展示）**之外**的 401 一律视为会话失效：清令牌 + 广播；`app/SessionExpiryWatcher` 收到后提示并跳登录页。

## 命令

```bash
pnpm dev      # dev server（端口 40000）
pnpm build    # tsc -b && vite build
pnpm lint     # eslint
```

## 已知问题

- 本环境 **vite 8.3.4 的 dev 下 `define` 未生效**（build 正常）——文档称 dev 应作为全局注入，实测未注入；版本注入改用 `typeof` 兜底（dev 显示 `'dev'`），记录见 `vite.config.ts` 注释。
