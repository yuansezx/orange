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
  - **系统壳 `AppShell`**：左侧只放用户视角的 **Workspace**（后台管理、音乐……）+ 用户区。系统侧栏 `SystemSidebar` 的 `hidden/rail/expanded` 三态归**系统统一管理**（全局一份，切换 workspace、进入个人中心都不重置）；workspace 只能用 `systemSidebarBehavior` 声明内容关系（`push` 挤占 / `overlay` 悬浮），**不能**控制系统侧栏形态。形态状态只在内存，不做持久化。
  - **Workspace 壳**（`WorkspaceLayout`）：在系统内容区里展开，默认 = `WorkspaceSidebar`（workspace 级导航）+ workspace 内容区 + `WorkspaceContextPanel`（detail / trends / ranking 等，非模态 overlay，不锁背景）。需要自定义结构的 workspace（如播放器）在 `WorkspaceRef.layout` 提供组件、自行渲染 `<Outlet />`；系统壳与 `WorkspaceThemeProvider` 仍在外层。**不加隐藏左/右栏开关**——定制走布局组件这一条路。
  - **FeatureModule 的三个贡献通道**：`workspace + groups`（用户侧，模块自己的 workspace）；`admin`（技术管理页，挂到平台统一的 `ADMIN_WORKSPACE`，完整路由 `/admin/{feature}/{path}`）；`settings`（个人中心 `/account/{feature}/{path}`）。用户侧完整路由为 `{workspace.basePath}/{feature}/{path}`（如 `/toolbox/tools/tasks`）；没有导航页，`/` 按权限落到第一个可访问页面。一个 feature 可以同时贡献 `groups` 和 `admin`；只有 `admin` 的 feature 也会被路由发现。**若 `workspace` 已经声明为 admin，不要再用 `admin` 通道**，否则同一 workspace 会重复挂载。
  - **个人中心**：系统级 `/account`，设置菜单由各 feature 的 `settings` 聚合，路径 `/account/{feature}/{path}`。
  - 菜单项不带 `permission` = 永远可见；过滤只是 UX，后端 403 兜底。
- **后台管理（admin）的语义**：平台**技术管理**入口（monitor、系统配置、模块技术配置），不是所有管理页的容器。模块业务运营/数据管理（如 tools 的全部任务）留在模块 workspace，用权限做「我的 / 全部」视图切换；iam 主业务默认不视为技术管理，只有技术配置类页面才进 admin。`ADMIN_WORKSPACE`（`@shared/navigation`）是它的唯一定义；monitor 是 `admin` 通道的标准范例。**iam 目前仍整体用 `workspace: ADMIN_WORKSPACE` 住在后台管理，归属未定，不要当标准写法**。
- **Workspace 的定义与布局**：没有中央注册表。每个 feature 在 `index.ts` 声明 `workspace: WorkspaceRef`（平台级 workspace 用 `ADMIN_WORKSPACE` 常量），`app/routes.ts` 按 `key` 聚合并合并 `theme`/`layout`（首个 feature 定 icon，`layout` 以最后声明为准）。默认用 `app/layout/WorkspaceLayout`（侧栏 + 内容 + context panel）；自定义结构在 `WorkspaceRef.layout` 提供组件并自行渲染 `<Outlet />`，系统壳与 `WorkspaceThemeProvider` 仍在外层。
- **workspace 可见性**：没有 workspace 级权限；`filterWorkspacesByPermission` 按菜单项 `permission` 推导，至少一个可见菜单才显示 workspace（超管旁路）。workspace 是聚合入口，不是权限边界。
- **非平台模块目录链接**：`web/src/features/*` 下的目录链接由 `vite.config.ts` 的 `modulePathPlugin` 自动发现；解析到仓外真实路径的模块 id 会改写回宿主链接路径，保证模块内裸依赖（antd / dayjs…）从 `web/node_modules` 解析，dev 与 build 一致。`ORANGE_MODULE_ROOTS` 仅作 dev server `fs.allow` 兜底。
- **features 对齐后端模块**：模块型切片与后端模块**同名同边界**（`iam` / `monitor`…），**不按"iam 的某张表"平铺**（否则 iam 专属的共享件无处安放）；控制台级切片（`auth`）例外。例：`features/iam/user`。
- **用户身份展示（按空间富余度分层）**：`username` 是稳定标识，`nickname` 是可长可变的展示名。
  - **高密度列表 / 审计流**（表格创建人·删除人、审计日志列表、在线会话、确认弹窗）：**只显示 `username`**，nickname 不占识别位；
  - **用户自身列表**：桌面保留「用户名 / 昵称」两列；移动卡片只 `username`，nickname 进详情；
  - **选择器**（用户下拉、成员管理）：`昵称（username）`（认人优先，长昵称省略）；
  - **详情**：username / nickname 分成独立字段；单行引用用 `username（nickname）`；
  - **个人中心**：保留 `nickname` 主 + `@username` 次（自我展示语境）。
  - 括号统一全角；`@username` 只用于个人展示，不混入管理列表。格式化函数收口在 `shared/ui/userLabel.ts`。
- **平台分叉**：**默认一份响应式实现**；`shared/platform` 的 `<Platform desktop={} mobile={}/>` 是**逃生口、按需用**。判据：同一行为、不同长相 → 共用；不同行为 → 才拆。跨端**共用**组件放 `components/` **根目录**，只有**确实分叉**的才进 `components/desktop/` `mobile/`；取数等逻辑放页面层共用、视图只渲染。范例：`features/iam/user`（一处叶子分叉）；系统壳本身也是分叉——桌面 = 系统侧栏 `SystemSidebar`（三态）+ 内容（workspace 自管左中右），移动 = 顶栏（汉堡）+ workspace 抽屉 + 内容；个人中心暂用顶部设置选择器。
- **服务器状态**用 TanStack Query；`shared/api` 只出 `get/post/put/del<T>`，错误统一归一为 `ApiError`（`code` 对齐后端错误体，可 `except`/按 `code` 区分）。
- **配置**：值是**数据**，放 `src/config.json`；读取层 `shared/config/index.ts` 只"读数据 + 定型"，不含配置值。`appVersion` 构建期从 `package.json` 注入（`__APP_VERSION__`），dev 未注入时 `typeof` 兜底 `'dev'`。
- **配色收敛**：颜色一律走 **`@shared/theme/tokens`**（**唯一来源**），组件里**别写死 hex**；antd 主题 `app/theme.ts` 也引同一份 token。**多套方案**放在 `colorSchemes`，**当前生效**的由 `config.json` 的 `colorScheme` 选定（改值 → 重新构建，构建期非运行时）；消费方一律引 `colorTokens`。之所以自建而非用 antd 的 CSS 变量：本项目同时用 antd 与 antd-mobile（两套主题系统），需要两家之上的共同来源才能收敛到一处。**角色分工**：`brand` 只做品牌露出（logo/品牌名/光斑），`brandAction` 才当交互色（主按钮/链接，满足对比度），`brandActionText` 管主按钮里的文字色；工作区用**低饱和画布** `bgLayout` + 容器 `bgContainer`，两级左栏分别用 `bgSystemSidebar` / `bgWorkspaceNav`（可独立调色），`brandSoft` 只留给品牌面（登录页）。**选中态用成对 token `navSelectedBg` / `navSelectedText`**（允许黑底白字的反色方案），组件直接套用，**不得**用品牌色/白底自行推导。下拉/树的选中项是例外：浅色方案沿用 antd 派生（浅底深字，hover 变亮仍可读），反色方案才在 `colorSchemes` 显式声明 `selectionBg` / `selectionText`（antd 派生的选中 hover 是独立 token，统一套 nav pair 会让浅色方案 hover 过亮）。**workspace 级配色**用 `WorkspaceRef.theme`（`WorkspacePalette`：左栏/画布/容器/边框/文字/交互色）覆盖，缺省回退 `defaultWorkspacePalette`。`WorkspaceLayout` 用 `WorkspaceThemeProvider`（context + 嵌套 `ConfigProvider`）把调色板作用于整个 workspace：内联样式用 `useWorkspacePalette()`，antd 组件自动跟随；**系统壳在 provider 之外，始终走全局品牌配色**。语义色（成功/错误/警告）跨 workspace 保持一致。注意 antd `Menu` 默认用 `colorBgContainer` 刷根背景，侧栏菜单必须显式传底色。
- **语义 Tag 的强调边界**：**结果导向、需要一眼识别**的信息（如审计日志的成功/失败）用 **Presets (solid)** + 库预设原色（`variant="solid"`，成功 `green`、失败 `error`）；**仅告知、偏装饰性**的详情状态用默认 **filled**（浅底深字），成功色走 `shared/theme/tokens` 的 `semanticColors`（低饱和深绿）。判据是「用户是否急着在大量内容里找结果」，不是信息本身重不重要；列表里的启用/停用是 Switch，不走 Tag。
- 别名：`@app` / `@shared` / `@features` / `@`（见 `vite.config.ts` 与 `tsconfig.app.json`）。

## 对接后端

- dev 走 vite **proxy**：`/api` → `http://127.0.0.1:41000`（后端不做 CORS，部署走 nginx）。dev server 的 host/port 与 proxy 目标均可用 `web/.env` 的 `ORANGE_DEV_HOST` / `ORANGE_DEV_PORT` / `ORANGE_API_PROXY_TARGET` 覆盖，默认值在 `vite.config.ts`、模板见 `web/.env.example`（`.env` 不入库）。
- 路由前缀 `/api/{module}`（iam 即 `/api/iam`，如 `/api/iam/auth/login`、`/api/iam/users`）；`Authorization: Bearer` 认证。
- 部门选择器统一用 `GET /api/iam/depts/visible`（登录即可、按数据范围过滤的精简 id/name 树）；管理端 `GET /api/iam/depts/tree` 需要 `iam:dept:read`，只给部门管理页。
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
