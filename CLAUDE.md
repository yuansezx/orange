# Orange 项目指南

## 项目概述

**单 FastAPI app + 多模块**的平台。当前仅有一个业务模块：**iam**（Identity and Access Management）。
多 app（一个进程挂多个 FastAPI 实例）的场景另起项目，不并入本仓库。

架构底色是**六边形（ports/adapters）+ 分层**；DDD 按模块分级使用（默认轻量），iam 是学习载体。

## 技术栈

- Python 3.13+ / 包管理 `uv`
- FastAPI（lifespan + 全局异常处理）；`app:create_app` 工厂 + uvicorn `factory=True`
- pydantic / pydantic-settings（分节 YAML（`core` / `iam`）+ `.env`，`YamlConfigSettingsSource`）
- Tortoise-ORM（`asyncpg` 驱动）+ **aerich**（迁移）；**tzdata**（Windows 无系统时区库）
- loguru（异步日志，分级输出）；future-uuid（UUIDv7）；bcrypt（密码哈希）；pyjwt + redis（令牌，待补全）

## 项目结构

```
app/
├── __init__.py                    # FastAPI 应用工厂 create_app() + lifespan（无模块级副作用）
├── core/                          # 全局共享基础设施（无业务语义）
│   ├── __init__.py                #   init_logger() / get_event_bus() / start()（含模块 bootstrap 编排）/ stop()
│   ├── domain/                    #   DDD 领域抽象
│   │   ├── entities.py            #     AuditableEntity[IdType]（含软删除字段）
│   │   ├── events.py              #     BaseEvent
│   │   ├── event_bus.py           #     EventBus / EventHandler
│   │   ├── repositories.py        #     BaseRepository：get/create/bulk_create/update/hard_delete
│   │   ├── units_of_work.py       #     TransactionContext / InTransactionType
│   │   └── value_objects.py       #     BaseEntityId（value: uuid.UUID + new()）/ EventId
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
│   └── utils/                     #     schemas(PageResult) / validators / type_utils / jwt_util / password_hash
├── iam/                           # 身份与访问管理模块
│   ├── __init__.py                #   DB_CONNECTION = 'default'（本模块用的逻辑连接名，core 按约定读）
│   ├── bootstrap.py               #   模块启动钩子：超管种子 + 资源/权限目录声明（core 按约定调用）
│   ├── domain/
│   │   ├── shared/                #     enums.py / value_objects.py / exceptions.py
│   │   ├── user/                  #     entities.py / enums.py / repositories.py / services.py / exceptions.py
│   │   ├── role/                  #     entities.py / enums.py / repositories.py / services.py / exceptions.py
│   │   ├── dept/                  #     entities.py / repositories.py / services.py
│   │   ├── resource/              #     entities.py / repositories.py / exceptions.py
│   │   ├── permission/            #     entities.py / repositories.py / exceptions.py
│   │   ├── user_role_assignment/  #     entities.py / repositories.py
│   │   ├── login_log/             #     entities.py
│   │   └── current_user/          #     entities.py / repositories.py（当前用户缓存）
│   ├── application/
│   │   ├── common/               #     exceptions.py / dto.py（EffectivePermissions）/ queries.py（EffectivePermissionQuery，CQRS 读侧）
│   │   ├── current_user/          #     dto.py / services.py（CurrentUserApplicationService）/ ports.py（TokenManagerPort）/ event_handlers.py
│   │   ├── user/                  #     dto.py / services.py（UserApplicationService）/ exceptions.py
│   │   ├── resource/              #     dto.py / services.py（ResourceApplicationService）/ exceptions.py
│   │   ├── role/                  #     dto.py / services.py（RoleApplicationService）/ exceptions.py
│   │   └── user_role_assignment/  #     services.py
│   ├── infrastructure/
│   │   ├── settings.py            #   IAMSettings / JWTConfig / CurrentUserConfig / IAM_SETTINGS
│   │   ├── adapters/              #   端口实现：token_manager_adapter.py（JWT + Redis 白名单）
│   │   ├── cache/                 #   current_user_repo.py（CurrentUserRepositoryRedisImpl）
│   │   └── persistence/tortoise/{dialect}/  # 按方言分目录（后端解耦）
│   │       ├── models/            #     __init__.py / user.py / dept.py / ...（每实体一文件）
│   │       ├── repositories/      #     __init__.py / user.py / ...（聚合仓储，含 领域↔表 映射）
│   │       └── queries/           #     effective_permission.py（EffectivePermissionQueryTortoiseImpl，CQRS 读侧查询）
│   └── interface/
│       ├── dependences.py         #   组合根：get_*（http / bootstrap / python api 共用）
│       └── http/user/             #   api.py / schemas.py
├── interface/                     # app 级接口层（HTTP 边界；app 全局，非模块级）
│   └── http/exception_handlers.py #   异常→HTTP 映射 + 统一错误体
├── run.py                         # 启动入口（uvicorn 工厂 + 读配置）
├── scripts/migrate.py             # 手动迁移入口（uv run python -m scripts.migrate）
├── pyproject.toml
├── config_example.yaml            # 配置示例（core / iam 分节）
└── CLAUDE.md
```

## 架构规范

- **层依赖方向**：`interface → application → domain`；`infrastructure → domain`。`core` 不依赖任何业务模块。
- **配置**：分节 YAML（`core` / `iam`）+ `.env`；优先级 **`init > env > dotenv > yaml > secret`**（env 高于文件，容器里可用环境变量覆盖）。
  - `core` 段：`app_name`、`debug`、`host`/`port`、`logs_dir`、**`modules`**（启用模块清单）、`persistence`
  - `persistence`：`backend`（ORM）+ `auto_migrate` + `use_tz`/`timezone` + `options`（**连接映射** `{连接名: {dialect, credentials}}`；每个连接**自带引擎** `dialect`，`engine` 由方言层补、不写进配置）
- 实体用 pydantic `BaseModel`；值对象用 `@dataclass(frozen=True)`（带 `__post_init__` 校验 + 脱敏 property）。
- **实体 ID**：`BaseEntityId`（持有 `uuid.UUID`）及其子类 `UserId`/`RoleId`/`DeptId`/`UserRoleId`/`ResourceId`/`PermissionId`/`EventId`；用 `XxxId.new()` 生成（UUIDv7）。**不设 IdProvider 端口**。
- `AuditableEntity[IdType]` 泛型审计基类（created/updated/deleted 的 at/by）。
- 仓储继承 `BaseRepository`：`get / create / bulk_create / update / hard_delete`。
- **删除语义统一**：`delete` = **软删**（实体方法，置 `status=DELETED`+`deleted_at/by`）；`hard_delete` = **物理删**（仓储）；`evict` = 缓存淘汰。**裸 `delete` 绝不表示物理删除。**
- 枚举统一 `str, Enum` 且以 `Enum` 结尾（`StatusEnum`、`UserTypeEnum`、`DataScopeEnum`）。
- **异常与响应**：两条根（`core.exceptions`：`InfrastructureBaseException` 技术中立 / `BusinessBaseException` 业务合一）+ 统一错误体 `{code,message,details}`；HTTP 映射见 `app/interface/http/exception_handlers.py`。详见「异常与 HTTP 响应」。
- `PageResult[DataType]`（`core/utils/schemas.py`）；`check_unique` / `check_data_scope`（`core/utils/validators.py`）。
- interface/schemas 可直接引用 domain 值对象作字段类型（pydantic 自动走 `__post_init__`）。
- 应用服务接 DTO（`CreateUserIn` 等）并调用领域服务完成业务逻辑。
- **事务**：`TransactionContext` + `InTransactionType`（DI）；实现由持久化后端提供，经 `core.infrastructure.persistence.get_in_transaction()` 取用；应用层 `async with in_transaction():`（tortoise 事务连接按 task ContextVar 自动绑定）。
- **领域事件**：`EventBus` / `EventHandler` 抽象，`BaseEvent` 在 `core/domain/events.py`。
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
- **组合根**：`app/{模块}/interface/dependences.py` 提供 `get_*`，由 http（FastAPI `Depends`）、bootstrap、python api 共用。
- **抽象取舍判据**：Port 只在「**触碰外部（IO/第三方）**」或「**测试要替换**」时才抽；纯计算/纯数据**不抽**（直接函数/值对象）。
- **包 `__init__` 不放重副作用、也不放会拖入其它层的 import**（判据是"导入的耦合/成本"，非"有无副作用"）：模块启动钩子（有副作用）独立成 `bootstrap.py`；依赖其它层类型的声明（如资源目录，依赖 application DTO）也放 `bootstrap.py`（否则 `import app.{模块}.domain.*` 会连带拖入 application/循环导入）；**纯常量**（如 `DB_CONNECTION`，零依赖零副作用）可放 `__init__`。FastAPI app 用工厂而非模块级实例。
- **领域规则收口在实体**（防漂移）：如 `User` 的 nickname 缺省=username、非超管不得使用保留用户名（`admin`）。
- **资源/权限目录（iam RBAC）**：资源=名词（`module` 分组、扁平无层级），权限=资源×操作；权限标识 `module:resource:action`（如 `iam:user:create`），完整 key 运行时派生、不落库；`(module,code)` 与 `(resource_id,action)` 唯一。
- **角色（iam）**：`code` 为唯一标识（不可改），`name` 仅作昵称。角色聚合跨三表：`iam_role` + 关系表 `iam_role_permission` / `iam_role_dept`（**裸映射：无 status/审计，移除即物理删**）。**聚合根 `Role` 持有 `permission_ids` / `custom_dept_ids`（其他聚合的 id 引用，非对象）**，由 `RoleRepository` 整体装配/保存（`get`/`get_all` 连带集合，`create`/`update` 连带落库，关系做差集替换）；**跨聚合不级联**，一致性靠读路径按 ACTIVE 过滤。`user_role` 才是实体（因需用户自助 DISABLED 某条授权；时限也挂它），**一行/状态翻转：`UNIQUE(user_id, role_id)`，重加曾移除的角色复活已删行、不新插**。
- **鉴权/令牌（iam）**：令牌 = JWT（自包含 `exp`）+ Redis **白名单** `iam:user_tokens:{uid}`（hash：token→⊥，**HEXPIRE** 每 field 独立 TTL）；多端=多 field，单端 `HDEL`、全端 `DEL`。CurrentUser **快照** `iam:current_user:{uid}`（独立短 TTL）：权限变更只清快照、会话不掉线，快照缺失则重解析回填。有效权限由 `EffectivePermissionQuery.resolve`（**应用层 common 的查询**，非聚合仓储）**唯一收口**（逐级按 ACTIVE 过滤）。Redis 由 **core 门面** 管理（`core.cache`，同 persistence；未配置则不启动）。

### 命名约定

- **自定义 / 第三方依赖的抽象**：接口用 `XxxPort`（`ports.py`），实现用 `XxxAdapter`（`adapters/xxx_adapter.py`）——对应六边形 Port/Adapter。
- **DDD 原生抽象**（`Repository` / `EventBus` / `UnitOfWork`）：沿用 DDD 词汇命名接口，实现以 `XxxImpl` 结尾（如 `EventBusMemoryImpl`、`UserRepositoryTortoiseImpl`）。
- **纯计算工具**：直接放 `core/utils/`（函数或简单类，如 `password_hash`、`JWTUtil`），**不套 Port**。
- **数据类型的归属按语义定**（不按谁先用）：领域概念 → domain（entity / 值对象）；应用层通用数据（含查询结果）→ `dto.py`；端口私有契约类型 → 与端口同处 `ports.py`（过长时拆 `ports/` 包，一端口一文件）。
- **查询（CQRS 读侧）不与聚合仓储混放**：跨聚合只读查询放**应用层**（接口 `common/queries.py`，实现 `infrastructure/persistence/tortoise/queries/`）；`repositories/` 只留聚合仓储（entity ↔ 表）。
- 枚举统一 `XxxEnum`，且 `str, Enum`。

### 异常与 HTTP 响应

> 以下为**当前取舍**，随需求可变；调整时同步本节。

**两条根**（都在 `core/exceptions.py`，层中立、纯定义）：
- `InfrastructureBaseException`——**技术中立**。基础层负责「库异常 → 本族」，**跨边界禁止抛第三方库类型**。兜底就是根本身，某关切真实到要单独 catch 时才加子类。基础设施**不主动**包装库异常（默认让存储/缓存异常冒成 500、当 bug 处理），确有业务需要时才就地包。端口特有的中立异常继承本族、**放该 port 的 `ports.py`**（如 `TokenVerificationException`）。
- `BusinessBaseException`——**业务**。domain 与 application **合一**（不再分两棵）。类级 `code`（稳定机读码）+ 类级 `kind`（`ErrorKindEnum` 语义类别）+ 实例级可选 `details`。

**翻译职责**（不许混）：基础层做「库异常 → 中立」；应用层做「中立 → 业务」（**唯一**做这跳的地方；仅当它有业务含义时）。**基础设施层不许 import 业务异常**（端口接口例外，可 lint）。

**HTTP 映射**（`app/interface/http/exception_handlers.py`）：`kind →` VALIDATION/400、UNAUTHENTICATED/401、FORBIDDEN/403、NOT_FOUND/404、CONFLICT/409；技术/未捕获 → 500（不泄露内部、日志带堆栈）。归一 `RequestValidationError`（422）与 `HTTPException`。**统一错误体** `{code, message, details}`；**成功侧不套信封**，直接返数据、语义由 HTTP 状态码承担。

**异常归属**：具体业务异常按**语义**放各子域（`domain/*/exceptions.py`、`application/*/exceptions.py`）；模块业务根 `IAMBusinessBaseException` 在 `iam/domain/shared/exceptions.py`。

**跨模块（python api）**：只经 **core 共享内核**通信——调用方 `except BusinessBaseException` + 按 `code` 区分；**模块根不对外发布**，iam 的 `interface/` 只发布 `get_*`（+ 可选 code 词表），不发布异常类型。故 **`code` 须当稳定接口**（前缀命名空间、不随意改）。可逆：将来要从 `interface/` 暴露模块根即可，不破坏既有代码。

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
