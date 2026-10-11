# Orange 前端（web）指南

管理台前端：**登录页 → 按权限显示各模块入口的导航页 → 模块自己的首页**。
与后端同仓（后端在 `app/`，见根 `CLAUDE.md`）；前后端同仓、单 git 仓。

## 技术栈

- Vite + React 19 + TypeScript；包管理 `pnpm`
- 路由 `react-router-dom` v7
- **服务器状态** TanStack Query v5；**客户端状态** zustand
- UI：`antd`（桌面）+ `antd-mobile`（移动）
- HTTP `axios`；表单 `react-hook-form` + `zod`

## 目录结构

```
web/src/
├── app/        # 组合根（= 后端 app 工厂）：providers / router / routes / layout（桌面/移动）
├── shared/     # 共享内核（= 后端 core，无业务语义）：api / platform / query / ui / lib / config / auth / navigation
└── features/   # 切片，两类：
    ├── <模块>/           # ① 模块型：对齐后端模块（iam / portal / monitor…）
    │   ├── <页面>/       #    每个页面：api / hooks / components / types.ts / routes.ts
    │   ├── components/   #    模块内共用件（如部门选择器）——留模块内，别上浮到 shared
    │   └── index.ts      #    门面：导出 FeatureModule（聚合本模块的 routes + nav）
    └── <控制台级>/       # ② 控制台级：不属任何后端模块（auth 登录、home 概览）
        └── index.ts      #    同样导出 FeatureModule
```

## 约定

- **依赖单向**：`app → features → shared`。feature 不认识 app；跨 feature 只能经其**门面** `@features/<name>`，**禁止深入内部路径**——由 ESLint `no-restricted-imports` 强守（见 `eslint.config.js`）。
- **模块自报门面**：feature 只在 `index.ts` 导出 `FeatureModule`（`routes` + `nav`）；组合根 `app/routes.ts` 逐个登记（同后端 `core.modules`）。
- **features 对齐后端模块**：模块型切片与后端模块**同名同边界**（`iam` / `portal` / `monitor`…），**不按"iam 的某张表"平铺**（否则 iam 专属的共享件无处安放）；控制台级切片（`auth`/`home`）例外。例：`features/iam/user`。
- **平台分叉**：**默认一份响应式实现**；`shared/platform` 的 `<Platform desktop={} mobile={}/>` 是**逃生口、按需用**。判据：同一行为、不同长相 → 共用；不同行为 → 才拆。跨端**共用**组件放 `components/` **根目录**，只有**确实分叉**的才进 `components/desktop/` `mobile/`；取数等逻辑放页面层共用、视图只渲染。范例：`features/home`（共用档）、`features/iam/user`（一处叶子分叉）。
- **服务器状态**用 TanStack Query；`shared/api` 只出 `get/post/put/del<T>`，错误统一归一为 `ApiError`（`code` 对齐后端错误体，可 `except`/按 `code` 区分）。
- **配置**：值是**数据**，放 `src/config.json`；读取层 `shared/config/index.ts` 只"读数据 + 定型"，不含配置值。`appVersion` 构建期从 `package.json` 注入（`__APP_VERSION__`），dev 未注入时 `typeof` 兜底 `'dev'`。
- **配色收敛**：颜色一律走 **`@shared/theme/tokens`**（**唯一来源**），组件里**别写死 hex**；antd 主题 `app/theme.ts` 也引同一份 token。**多套方案**放在 `colorSchemes`，**当前生效**的由 `config.json` 的 `colorScheme` 选定（改值 → 重新构建，构建期非运行时）；消费方一律引 `colorTokens`。之所以自建而非用 antd 的 CSS 变量：本项目同时用 antd 与 antd-mobile（两套主题系统），需要两家之上的共同来源才能收敛到一处。
- 别名：`@app` / `@shared` / `@features` / `@`（见 `vite.config.ts` 与 `tsconfig.app.json`）。

## 对接后端

- dev 走 vite **proxy**：`/iam` → `http://127.0.0.1:41000`（后端不做 CORS，部署走 nginx）。
- 路由前缀 `/{module}`（iam 即 `/iam`，如 `/iam/auth/login`、`/iam/users`）；`Authorization: Bearer` 认证。
- 错误体统一 `{code, message, details}`（成功侧不套信封）。
- 后端未就绪时用 mock：`shared/lib/env.ts` 的 `USE_MOCK`（dev 默认开；设 `VITE_USE_MOCK=false` 关）。

## 命令

```bash
pnpm dev      # dev server（端口 40000）
pnpm build    # tsc -b && vite build
pnpm lint     # eslint
```

## 已知问题

- 本环境 **vite 8.3.4 的 dev 下 `define` 未生效**（build 正常）——文档称 dev 应作为全局注入，实测未注入；版本注入改用 `typeof` 兜底（dev 显示 `'dev'`），记录见 `vite.config.ts` 注释。
