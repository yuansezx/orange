# Orange 项目指南

## 项目概述

**单 FastAPI app + 多模块**的平台。当前业务模块：**iam**（Identity and Access Management）；**monitor**（审计日志，后续接系统日志）已接入骨架与 audit_log 直写。
多 app（一个进程挂多个 FastAPI 实例）的场景另起项目，不并入本仓库。

架构底色是**六边形（ports/adapters）+ 分层**；DDD 按模块分级使用（默认轻量），iam 是学习载体。

**仓库结构**：`app/`（后端，本文件详述）+ `web/`（前端 React 管理台，约定见 **`web/CLAUDE.md`**）。前后端同仓、单 git 仓。

## 技术栈

- Python 3.13+ / 包管理 `uv`
- FastAPI（lifespan + 全局异常处理）；`app:create_app` 工厂 + uvicorn `factory=True`
- pydantic / pydantic-settings（分节 YAML（`core` / `iam`）+ `.env`，`YamlConfigSettingsSource`）
- Tortoise-ORM（`asyncpg` 驱动）+ **aerich**（迁移）；**tzdata**（Windows 无系统时区库）
- loguru（异步日志，分级输出）；future-uuid（UUIDv7）；bcrypt（密码哈希）；pyjwt + redis（令牌 = JWT + Redis 白名单）

## 项目结构

```
app/                               # 后端（本文件详述）；仓库根另含 web/（前端）、run.py、scripts/、pyproject.toml、config_example.yaml、CLAUDE.md
├── __init__.py                    # FastAPI 应用工厂 create_app() + lifespan（按 core.modules 动态挂载各模块 router）
├── core/                          # 全局共享基础设施（无业务语义）
│   ├── __init__.py                #   init_logger() / get_event_bus() / start()（含模块 bootstrap 编排）/ stop()
│   ├── domain/                    #   DDD 领域抽象
│   │   ├── entities.py            #     AuditableEntity[IdType]（含软删除字段）
│   │   ├── events.py              #     BaseEvent
│   │   ├── event_bus.py           #     EventBus / EventHandler
│   │   ├── repositories.py        #     BaseRepository：get/create/bulk_create/update/hard_delete
│   │   ├── units_of_work.py       #     TransactionContext / InTransactionType
│   │   └── value_objects.py       #     SingleValueObject（RootModel）/ BaseEntityId（root: uuid.UUID + value/new()）/ EventId
│   ├── application/               #   core 的应用层数据
│   │   └── dto.py                 #     RequestMeta（请求级技术元数据：request_id / ip / user_agent）
│   ├── infrastructure/
│   │   ├── settings.py            #     AppBaseSettings / CoreSettings / CORE_SETTINGS（含 persistence / cache 段）
│   │   ├── event_bus_impl.py      #     EventBusMemoryImpl
│   │   ├── persistence/           #     持久化（后端中立门面 + 具体后端）
│   │   │   ├── __init__.py        #       start/stop_persistence、run_persistence_migrations、get_in_transaction
│   │   │   └── tortoise/          #     ORM 后端
│   │   │       ├── tortoise_backend.py  # init / close / run_migrations + TortoiseTransactionContext
│   │   │       ├── models.py            # AuditableModel（ORM 审计基类，abstract）
│   │   │       └── postgres/postgres_backend.py  # DB 方言层（{dialect}/）：build_connection 补 engine
│   │   └── cache/                 #     缓存（与 persistence 同构的门面：cache/{backend}/{backend}_backend）
│   │       ├── __init__.py        #       start_cache / stop_cache / get_cache
│   │       └── redis/redis_backend.py
│   ├── exceptions.py              #     异常两根 + ErrorKindEnum（纯定义，不依赖 fastapi）
│   ├── utils/                     #     schemas(PageResult) / validators / type_utils / jwt_util / password_hash
│   └── interface/                 #     接口层（core 自己的 HTTP 边界）——与业务模块的 {模块}/interface/ 同构
│       └── http/                  #   exception_handlers.py（异常→HTTP）/ dependencies.py（get_request_meta）
├── iam/                           # 身份与访问管理模块
│   ├── __init__.py                #   DB_CONNECTION = 'default'（本模块用的逻辑连接名，core 按约定读）
│   ├── bootstrap.py               #   模块启动钩子：超管种子 + 资源/权限目录注册 + 订阅 CurrentUser 快照失效（core 按约定调用）
│   ├── domain/
│   │   ├── shared/                #     enums.py / value_objects.py / exceptions.py / services.py（DataScopeService）
│   │   ├── user/                  #     entities.py / enums.py / repositories.py / services.py / exceptions.py / events.py
│   │   ├── role/                  #     entities.py / enums.py / repositories.py / services.py / exceptions.py / events.py
│   │   ├── dept/                  #     entities.py / repositories.py / services.py / exceptions.py / events.py
│   │   ├── resource/              #     entities.py（Resource 聚合根 + 内嵌 Permission 实体）/ repositories.py / enums.py / exceptions.py / events.py
│   │   ├── user_role_assignment/  #     entities.py / repositories.py / events.py
│   │   ├── login_log/             #     entities.py
│   │   └── current_user/          #     entities.py（CurrentUser.has_permission / data_scope_spec）/ repositories.py（当前用户缓存）
│   ├── application/
│   │   ├── common/               #     decorators.py / exceptions.py / dto.py / queries.py / services.py / ports.py（审计写入端口）
│   │   ├── current_user/          #     dto.py / services.py（CurrentUserApplicationService）/ ports.py（TokenManagerPort）/ event_handlers.py（快照失效订阅）
│   │   ├── user/                  #     dto.py / services.py（UserApplicationService）/ exceptions.py
│   │   ├── dept/                  #     dto.py / services.py（DeptApplicationService）/ exceptions.py
│   │   ├── resource/              #     dto.py / services.py（ResourceApplicationService）/ exceptions.py
│   │   ├── role/                  #     dto.py / services.py（RoleApplicationService）/ exceptions.py
│   │   └── user_role_assignment/  #     services.py
│   ├── infrastructure/
│   │   ├── settings.py            #   IAMSettings / JWTConfig / CurrentUserConfig / IAM_SETTINGS
│   │   ├── adapters/              #   端口实现：token_manager_adapter.py（JWT + Redis）/ audit_log_writer_adapter.py（审计防腐）
│   │   ├── cache/                 #   current_user_repo.py（CurrentUserRepositoryRedisImpl）
│   │   └── persistence/tortoise/{dialect}/  # 按方言分目录（后端解耦）
│   │       ├── models/            #     __init__.py / user.py / dept.py / ...（每实体一文件）
│   │       ├── repositories/      #     __init__.py / user.py / ...（聚合仓储，含 领域↔表 映射）
│   │       └── queries/           #     effective_permission.py / dept_affected_users.py / permission_exists.py（CQRS 读侧查询）
│   └── interface/
│       ├── dependences.py         #   组合根：get_*（http / bootstrap / python api 共用）
│       ├── python/                #   对外 Python API（其他模块只经此调用；如 register_module_resources）
│       └── http/
│           ├── router.py          #     模块路由汇总（app 工厂按模块动态 include）
│           ├── dependencies.py    #     get_current_user（Bearer → CurrentUser，只做身份提取）
│           ├── user/              #     api.py（user_router）/ schemas.py
│           ├── dept/              #     api.py（dept_router）/ schemas.py
│           ├── role/              #     api.py（role_router）/ schemas.py
│           └── resource/          #     api.py（resource_router）/ schemas.py
├── monitor/                       # 监控与审计模块
│   ├── __init__.py                #   DB_CONNECTION = 'default'
│   ├── bootstrap.py               #   资源目录注册
│   ├── domain/audit_log/          #   AuditLog 实体 / 仓储接口 / 枚举
│   ├── application/audit_log/     #   AuditLogIn / GetAuditLogsIn / AuditLogOut / AuditLogApplicationService
│   ├── infrastructure/
│   │   └── persistence/tortoise/{dialect}/  # models（audit_log）/ repositories
│   └── interface/
│       ├── dependences.py         #   组合根
│       ├── python/audit_log.py    #   公开写入口 write_audit_log
│       └── http/                  #   health + audit_log 查询
```

## 架构规范

- **层依赖方向**：`interface → application → domain`；`infrastructure → domain`。`core` 不依赖任何业务模块。
- **配置**：分节 YAML（`core` / `iam`）+ `.env`；优先级 **`init > env > dotenv > yaml > secret`**（env 高于文件，容器里可用环境变量覆盖）。
  - `core` 段：`app_name`、`debug`、`host`/`port`、`logs_dir`、**`modules`**（启用模块清单）、`persistence`
  - `persistence`：`backend`（ORM）+ `auto_migrate` + `use_tz`/`timezone` + `options`（**连接映射** `{连接名: {dialect, credentials}}`；每个连接**自带引擎** `dialect`，`engine` 由方言层补、不写进配置）
- 实体与值对象统一用 pydantic：实体 `BaseModel`；值对象 `frozen=True`（校验用 `model_validator` / `field_validator`，脱敏等用 property）。**应用层 DTO 用普通 `BaseModel`，不加 `frozen`**（不可变/可哈希是值对象语义，DTO 不承担）。**项目内不用 dataclass 作为 DTO/值对象**。
- **值对象序列化（pydantic）**：单值 VO 继承 `SingleValueObject[value]`（`core/domain/value_objects.py`，基于 `RootModel`）——**出入裸值**（校验接受 裸值 / 同类型实例；嵌套序列化同为裸值），OpenAPI 展示为 `string`（`BaseEntityId` 带 `format: uuid`）。**构造传裸值**（如 `UserId(uuid)`），**读取用 `.value`**（领域访问器；`.root` 是 RootModel 实现细节，仅供值对象自身实现内部使用，外部调用端不用）。**多字段（结构化）VO 不套它**（如 `RoleSummary` / `DataScopeSpec`），用 frozen `BaseModel` 按对象序列化。
- **实体 ID**：`BaseEntityId`（持有 `uuid.UUID`）及其子类 `UserId`/`RoleId`/`DeptId`/`UserRoleId`/`ResourceId`/`PermissionId`/`EventId`；用 `XxxId.new()` 生成（UUIDv7）。**不设 IdProvider 端口**。
- `AuditableEntity[IdType]` 泛型审计基类（created/updated/deleted 的 at/by；`is_deleted` 是 `deleted_at` 的派生属性，不落库）。
- 仓储继承 `BaseRepository`：`get / create / bulk_create / update / hard_delete`。**删除选择收敛在仓储边界**：`get(id, include_deleted=False)` 与列表/过滤方法默认不返回已删对象（SQL 层过滤）；要看已删必须显式 `include_deleted=True` / `deleted=True`，应用层不做二次过滤。
- **删除语义统一**：`delete` = **软删**（实体方法，只写 `deleted_at/by`；**删除与业务状态正交**——`status` 只表可用性（`ACTIVE`/`DISABLED`），删除判别一律看 `deleted_at`，实体上 `is_deleted` 是派生属性）；`hard_delete` = **物理删**（仓储），悬空引用由**应用层**在同一事务内级联清理；`evict` = 缓存淘汰。**裸 `delete` 绝不表示物理删除。**
- **列表读约定**：读接口**默认只返回未删**（`deleted_at is null`）；回收站走**显式 `?deleted=true`**（只看已删）。仓储统一为 `get_all(status: StatusEnum | None = None, deleted: bool = False)`；`status` 只筛业务状态。**派生视图**（如 catalog）不受此约定约束——按用途只给可用项，且**停用（`DISABLED`）≠ 删除**、照常列出。
- **列表审计（iam）**：列表/详情响应带生命周期时间（属于数据 DTO）+ 操作人快照（`AuditOut` 嵌套 `{id, username, nickname}`；硬删操作人名字为 null 但 id 仍在）。列表用 `AuditService.build_many` 批量装配，避免 N+1。
- **回收站（iam）**：软删对象恢复走 `POST /{id}/restore`（复用 `*:delete`）；彻底删除走 `DELETE /{id}/hard-delete`（`*:hard_delete`，仅限已删，应用层级联清悬空引用）。部门恢复父删则拒、祖先非全活跃则自身落 `DISABLED`；部门彻底删除级联整棵已删子树。**资源删除只级联软删当时仍存活的权限**（已单独删的保留原删除时间）；**恢复只复活随资源一起删的那批**，单独删的权限留在权限回收站。权限彻底删除前先清角色引用。
- **启用 / 停用（iam）**：统一 `PUT /{users|roles|depts}/{id}/status`（body `{status}`，复用各自 `*:update`），与更新接口共用同一应用层状态变更逻辑（部门仍走 `_cascade_status` 级联）。**超管不能停用自己**（否则可能失去唯一能恢复系统的账号）。
- 枚举统一 `str, Enum` 且以 `Enum` 结尾（`StatusEnum`、`UserTypeEnum`、`DataScopeEnum`）。
- **异常与响应**：两条根（`core.exceptions`：`InfrastructureBaseException` 技术中立 / `BusinessBaseException` 业务合一）+ 统一错误体 `{code,message,details}`；HTTP 映射见 `app/core/interface/http/exception_handlers.py`。详见「异常与 HTTP 响应」。
- `PageResult[DataType]`（`core/utils/schemas.py`）；`check_unique`（`core/utils/validators.py`）。
- interface/schemas 可直接引用 domain 值对象作字段类型（pydantic 自动校验/序列化，裸值出入）。
- **请求元数据**：`RequestMeta`（`request_id` / `ip` / `user_agent`）在 `core/application/dto.py`；由 `core/interface/http/dependencies.py::get_request_meta` 从请求构造，**显式传给写用例**（不用中间件/ContextVar），不进 `CurrentUser` / 缓存。
- 应用服务接 DTO（`CreateUserIn` 等）并调用领域服务完成业务逻辑。
- **事务**：`TransactionContext` + `InTransactionType`（DI）；实现由持久化后端提供，经 `core.infrastructure.persistence.get_in_transaction()` 取用；应用层 `async with in_transaction():`（tortoise 事务连接按 task ContextVar 自动绑定）。
- **领域事件**：`EventBus` / `EventHandler` 抽象，`BaseEvent` 在 `core/domain/events.py`。**事件类按聚合归属放各子域 `domain/*/events.py`**（`UserChanged` / `RoleChanged` / `UserRolesChanged` / `DeptStructureChanged` / `ResourceChanged`）；**订阅者（副作用，如清 CurrentUser 快照）放应用层**（`application/current_user/event_handlers.py`）。资源/权限的状态、软删、恢复、硬删都会改变有效权限，故发 `ResourceChanged`（带受影响权限 id；硬删时预取受影响用户 id）清快照。进程内 `EventBusMemoryImpl` 是**临时实现**（`publish` fire-and-forget、不等 handler），预期后续接消息系统替换。
- **持久化（后端中立）**：只有 `infrastructure/persistence/` 内允许 import 具体 ORM；core 只通过门面访问。
  - 抽象层：`core/infrastructure/persistence/__init__.py`（`start/stop_persistence`、`get_in_transaction`）
  - 具体后端：`core/infrastructure/persistence/{backend}/{backend}_backend.py`
  - DB 方言：`core/infrastructure/persistence/{backend}/{dialect}/{dialect}_backend.py`（由**连接的 `dialect`** 选；把连接拼成 ORM 认的连接，补 `engine`）——**不同连接可用不同引擎**
  - **每模块连接**：模块在自己 `__init__.py` 声明 `DB_CONNECTION`（缺省 `'default'`），core 读取作该模块 app 的 `default_connection`；连接名→物理库由 config 的 `options` 绑定（**连接名 = dev 与 ops 的契约**）
  - **模块基础设施按方言分目录**：`app.{模块}.infrastructure.persistence.{backend}.{dialect}/{models,repositories,queries}`；`{dialect}` 由该模块连接的 `dialect` 决定（**models/queries/repositories 都按方言拆开**）。模型须在 `{dialect}/models/__init__.py` 汇总导出（否则 Tortoise 发现不到）
  - 组合根取方言实现：`core.infrastructure.persistence.module_infra(模块, 子模块)`（按模块的连接解析方言、动态导入）；组合根**不硬编码方言**
  - 迁移：aerich，`migrations/` **不入库**（版本账本在数据库 `aerich` 表）；`auto_migrate` 控制启动期是否迁移
- **模块 bootstrap**：`core.start()` 按 `core.modules` 动态 import `app.{模块}.bootstrap` 并调用其 `bootstrap()`（钩子可选）。core 只认约定，不认识具体模块。
  - **资源/权限目录声明固定放各模块自己的 `bootstrap.py`**（如 `IAM_RESOURCE_DECLARATIONS`），启动时幂等注册；不塞进包 `__init__`，也不散落在子包里。
  - **对账 pass**：注册后，本模块中**已无代码声明**的 `SYSTEM` 资源/权限自动**软删**并告警；软删保留 id，声明重新出现时复活同一行、角色授权自动恢复。`CUSTOM` 条目一律不碰。对账只软删；后台可手动硬删 `CUSTOM` 或**已软删的 `SYSTEM` 墓碑**（清理对账残留，重新声明会创建新 id）。
- **路由挂载**：core 不认模块。app 工厂按 `core.modules` 动态 import `app.{模块}.interface.http.router`（暴露 `router`）并 `include_router(prefix=f'{API_PREFIX}/{模块}')`（`API_PREFIX='/api'`，与前端路由/静态资源分离；**URL 版本 `/v1` 暂不做**，需要时只改该常量，不在 interface 层加版本目录）；模块未提供则跳过（判 `ModuleNotFoundError.name == path`，路由内部有真错则炸）。**每模块一个 `router`**（聚合各 resource 的 `<resource>_router`），resource 路由本体放 `interface/http/{resource}/api.py`。
- **组合根**：`app/{模块}/interface/dependences.py` 提供 `get_*`，由 http（FastAPI `Depends`）、bootstrap、python api 共用。
- **抽象取舍判据**：Port 只在「**触碰外部（IO/第三方）**」或「**测试要替换**」时才抽；纯计算/纯数据**不抽**（直接函数/值对象）。
- **包 `__init__` 不放重副作用、也不放会拖入其它层的 import**（判据是"导入的耦合/成本"，非"有无副作用"）：模块启动钩子（有副作用）独立成 `bootstrap.py`；依赖其它层类型的声明（如资源目录，依赖 application DTO）也放 `bootstrap.py`（否则 `import app.{模块}.domain.*` 会连带拖入 application/循环导入）；**纯常量**（如 `DB_CONNECTION`，零依赖零副作用）可放 `__init__`。FastAPI app 用工厂而非模块级实例。
- **领域规则收口在实体**（防漂移）：如 `User` 的 nickname 缺省=username、非超管不得使用保留用户名（`admin`）；`Dept.move_under` 的环路校验。
- **资源/权限目录（iam RBAC）**：资源=名词（`module` 分组、扁平无层级），权限=资源×操作；权限标识 `module:resource:action`（如 `iam:user:create`），完整 key 运行时派生、不落库；`(module,code)` 与 `(resource_id,action)` 唯一。**`Resource` 是聚合根，`Permission` 是其聚合内实体**（身份从属资源）——`ResourceRepository` 整体装配/保存（**读路径默认只装配未删权限；声明/写路径显式含软删行**以保 action 身份、按 id upsert 不删重建）；`Resource.delete` 级联软删其权限。两者各有 `resource_type` / `permission_type`（`SourceTypeEnum`：`SYSTEM` 代码声明 / `CUSTOM` 后台自建），供「对账」区分代码拥有与后建。**后台管理**：`/api/iam/resources`（列表/新建/更新/状态/软删/恢复/硬删）与 `/api/iam/permissions`（扁平列表/新建/更新/状态/软删/恢复/硬删）；列表含审计，资源列表含聚合内权限。**`SYSTEM` 条目后台只读**（可编辑字段、状态、软删、恢复均拒绝），但**已软删的 `SYSTEM` 墓碑允许彻底删除**（清理对账残留；重新声明会创建新 id、原角色授权不自动恢复），且允许在其下新增 `CUSTOM` 权限；`CUSTOM` 条目可管理。**权限回收站** = `GET /api/iam/permissions?deleted=true`：只列**资源仍存活**的已删权限（随资源删的跟着资源走，不单独出现）；资源恢复只复活随资源一起删的权限。
- **角色（iam）**：`code` 为唯一标识（不可改），`name` 仅作昵称。角色聚合跨三表：`iam_role` + 关系表 `iam_role_permission` / `iam_role_dept`（**裸映射：无 status/审计，移除即物理删**）。**聚合根 `Role` 持有 `permission_ids` / `custom_dept_ids`（其他聚合的 id 引用，非对象）**（`permission_ids` 引的是 Resource 聚合**内嵌实体**的 id——此处「跨聚合只引根 id」让位于「权限身份从属资源」），由 `RoleRepository` 整体装配/保存（`get`/`get_all` 连带集合，`create`/`update` 连带落库，关系做差集替换）；**跨聚合不级联**（**状态层面**：软删 / 禁用等状态变更不级联改其他聚合，一致性靠读路径按「未删 ∧ ACTIVE」过滤；**物理硬删**则显式级联清理从属行——无 FK，应用层做）。此约定的前提是「状态不级联**不影响业务判断**」，若日后发现有影响，软删也需级联（**待观察**）。`user_role` 才是实体（因需用户自助 DISABLED 某条授权；时限也挂它），**一行/状态翻转：`UNIQUE(user_id, role_id)`，重加曾移除的角色复活（清 `deleted_at`）已有行、不新插**。
- **部门（iam）**：部门树用**物化路径** `ancestors uuid[]`（根→父的祖先 id、不含自己）+ GIN 索引（Tortoise `contrib.postgres` 的 `ArrayField` / `GinIndex`）——找子孙走 `ancestors__contains`（`@>`）单查询。**移动**在应用层事务内连带重写子孙 `ancestors`，实体 `move_under` 做**环路校验**、`shift_descendant_ancestors` 重算子孙路径。**删除 = 级联软删整棵子树**（不允许「只删父、留子」，维持不变式「父已删 ⇒ 子必删」），子树内任一部门下有用户则整体拒绝。**状态级联**（不变式「子 ACTIVE ⇒ 祖先全 ACTIVE」）：停用 → **未删**子树全部 DISABLED；启用 → 祖先链中非 ACTIVE 者一并 ACTIVE（只校验**真正会被修改**的祖先的可写权限，防向上越权）；恢复时若自身 ACTIVE 但祖先非全活跃 → **自身落 DISABLED**（不惊动祖先）。已删子树保留删除前状态；状态变化不影响数据范围（解析不看 status），故不发结构事件。同级同名唯一：应用层校验 + DB `(parent_id,name)` 唯一索引兜底（**根部门 `parent_id` 为 NULL，DB 拦不住，靠应用层**）；且**软删仍占位**（唯一性检查显式 `include_deleted=True`），故恢复时不会撞名。结构变更（增/移/删）提交后发 `DeptStructureChanged`（携带受影响部门 = 旧/新父祖先链的对称差），供快照失效**精确定位**。
- **审计日志（monitor）**：`monitor_audit_log` **只追加**（无更新/软删）；动作码 `module:resource:action`，`resource` 是**聚合根码**（user / role / dept / resource / user_role / current_user），`target_type/target_id` 是具体对象；`summary` 人类可读，失败用 `error_code`（必填）+ `error_message`；`occurred_at` 业务发生时间，`persisted_at` 落库时间。写入经公开 Python API `write_audit_log` **在调用方业务事务内直接写 `audit_log`**（同库原子）；将来审计分库/接消息中间件时，由**生产方** outbox + relay 投递，monitor 作为消费方幂等落库（消费方不建 outbox）。查询：`GET /api/monitor/audit-logs`（权限 `monitor:audit_log:read`，支持 module/resource/action/operator/target/result/时间范围过滤 + 分页）。iam 的 user / role / dept / resource（含 permission）/ user_role 写用例已接入；登录/会话事件待登录记录方案确定。
- **令牌 / CurrentUser（iam）**：令牌 = JWT（自包含 `exp`）+ Redis **白名单** `iam:user_tokens:{uid}`（hash：token→⊥，**HEXPIRE** 每 field 独立 TTL）；多端=多 field，单端 `HDEL`、全端 `DEL`。CurrentUser **快照** `iam:current_user:{uid}`（`snapshot_ttl_seconds` 缺省 = 令牌期）：含 `roles` / `permission_codes` / `data_scope_spec`；**变更只清快照、会话不掉线**，快照缺失则重解析回填。有效权限由 `EffectivePermissionQuery.resolve`、数据范围由 `DataScopeService.resolve` 解析（均**应用层 common / domain 共享**，非聚合仓储）；快照失效由领域事件驱动（`application/current_user/event_handlers.py`）。Redis 由 **core 门面** 管理（`core.cache`，同 persistence；未配置则不启动）。
- **认证 / 授权（iam，双入口）**：**身份提取在接口层**（`interface/http/dependencies.py::get_current_user`，`Authorization: Bearer` → CurrentUser，缺/坏 → 401）；**授权判定是业务规则、收敛到 application**——功能权限 `current_user.has_permission(*groups)`（**逗号分隔的参数之间「或」、元组内「与」**（DNF）；超管旁路）、数据权限调 access service（`can_access`），**http 与 python api 两入口一致**。功能权限门禁可用 `@requires_permission(*groups)`（`application/common/decorators.py`，**同款与/或模型**；**空参定义期报错**；**按名绑定 `current_user` 参数**，缺参数亦定义期报错）；数据权限随对象变、需查库，仍手动调。接口层只做 `kind→状态码` 映射（403），**不判权限**。
- **数据权限（iam）**：数据范围在**快照构建时**解析成 `DataScopeSpec` 存进 `CurrentUser.data_scope_spec`（超管 → ALL；其余读「未删 ∧ ACTIVE」的 `user_role`→`role`，按「最宽松胜出、同模式并集」合并，`DEPT_AND_CHILD` 用部门树 `ancestors` 展开；无角色 / 仅 SELF → SELF）。读侧**直连** `current_user.data_scope_spec`（不再现场查库），仓储用 `scope_filter` 翻译成过滤条件。对象级判定走各 access service 的 `can_access`（`get_allowed_dept_ids` / `get_allowed_user_ids` / `get_allowed_role_ids`）。**角色不受数据范围管**；若要按部门管角色，需先有「数据可见性列」，未来再议。

### 命名约定

- **自定义 / 第三方依赖的抽象**：接口用 `XxxPort`（`ports.py`），实现用 `XxxAdapter`（`adapters/xxx_adapter.py`）——对应六边形 Port/Adapter。
- **DDD 原生抽象**（`Repository` / `EventBus` / `UnitOfWork`）：沿用 DDD 词汇命名接口，实现以 `XxxImpl` 结尾（如 `EventBusMemoryImpl`、`UserRepositoryTortoiseImpl`）。
- **纯计算工具**：直接放 `core/utils/`（函数或简单类，如 `password_hash`、`JWTUtil`），**不套 Port**。
- **数据类型的归属按语义定**（不按谁先用）：领域概念 → domain（entity / 值对象）；应用层通用数据（含查询结果）→ `dto.py`；端口私有契约类型 → 与端口同处 `ports.py`（过长时拆 `ports/` 包，一端口一文件）。
- **查询（CQRS 读侧）不与聚合仓储混放**：跨聚合只读查询放**应用层**（接口 `common/queries.py`，实现 `infrastructure/persistence/tortoise/queries/`）；`repositories/` 只留聚合仓储（entity ↔ 表）。
- 枚举统一 `XxxEnum`，且 `str, Enum`。
- **接口层 schema 命名**：HTTP 的 `schemas.py` 用 `XxxReq`（请求）/ `XxxResp`（响应）；应用层 DTO 用 `XxxIn` / `XxxOut`。两套不混用。

### 异常与 HTTP 响应

> 以下为**当前取舍**，随需求可变；调整时同步本节。

**两条根**（都在 `core/exceptions.py`，层中立、纯定义）：
- `InfrastructureBaseException`——**技术中立**。基础层负责「库异常 → 本族」，**跨边界禁止抛第三方库类型**。兜底就是根本身，某关切真实到要单独 catch 时才加子类。基础设施**不主动**包装库异常（默认让存储/缓存异常冒成 500、当 bug 处理），确有业务需要时才就地包。端口特有的中立异常继承本族、**放该 port 的 `ports.py`**（如 `TokenVerificationException`）。
- `BusinessBaseException`——**业务**。domain 与 application **合一**（不再分两棵）。类级 `code`（稳定机读码）+ 类级 `kind`（`ErrorKindEnum` 语义类别）+ 实例级可选 `details`。

**翻译职责**（不许混）：基础层做「库异常 → 中立」；应用层做「中立 → 业务」（**唯一**做这跳的地方；仅当它有业务含义时）。**基础设施层不许 import 业务异常**（端口接口例外，可 lint）。

**HTTP 映射**（`app/core/interface/http/exception_handlers.py`）：`kind →` VALIDATION/400、UNAUTHENTICATED/401、FORBIDDEN/403、NOT_FOUND/404、CONFLICT/409；技术/未捕获 → 500（不泄露内部、日志带堆栈）。归一 `RequestValidationError`（422）与 `HTTPException`。**统一错误体** `{code, message, details}`；**成功侧不套信封**，直接返数据、语义由 HTTP 状态码承担。

**异常归属**：具体业务异常按**语义**放各子域（`domain/*/exceptions.py`、`application/*/exceptions.py`）；模块业务根 `IAMBusinessBaseException` 在 `iam/domain/shared/exceptions.py`。

**跨模块（python api）**：模块的公开 Python API 统一放 **`interface/python/`**，其他模块只从 **infrastructure adapter** 调用它（application/domain 不 import 其他模块；基础设施依赖是可替换边缘，不是核心耦合）。调用方 `except BusinessBaseException` + 按 `code` 区分；**模块根与异常类型不对外发布**。故 **`code` 须当稳定接口**（前缀命名空间、不随意改）。

## 运行

```bash
# 起库（dev：暴露端口、独立口令与卷；base 版封在容器网段）
docker compose -f docker/docker-compose-base-dev.yaml --env-file docker/.env.dev up -d

uv run run.py                         # 起服务
uv run python -m scripts.migrate      # 手动迁移（auto_migrate 关闭时用）
```

**首个超管**：由 `iam/bootstrap.py` 硬编码初始化（`admin` / `admin123`，`need_change_password=True`，幂等——库中已有超管则跳过）。

## 命令/工具习惯

- 所有命令经 `uv` 执行，**不直接用 `python`**：
  - **根目录脚本**：`uv run <script>.py`（如 `uv run run.py`）
  - **子目录脚本**：`uv run python -m <包>.<模块>`（如 `uv run python -m scripts.migrate`）
    —— `sys.path[0]` 是脚本所在目录，子目录里直接跑会 `import app` 失败
