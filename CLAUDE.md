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
│   │   ├── settings.py            #     AppBaseSettings / CoreSettings / CORE_SETTINGS
│   │   ├── event_bus_impl.py      #     EventBusMemoryImpl
│   │   └── persistence/           #     持久化（后端中立门面 + 具体后端）
│   │       ├── __init__.py        #       start/stop_persistence、run_persistence_migrations、get_in_transaction
│   │       └── tortoise/
│   │           ├── tortoise_backend.py  # init / close / run_migrations + TortoiseTransactionContext
│   │           └── models.py            # AuditableModel（ORM 审计基类，abstract）
│   ├── exceptions.py              #     global_exception_handler + DomainBaseException/ApplicationBaseException
│   └── utils/                     #     schemas(PageResult) / validators / type_utils / jwt_util / password_hash
├── iam/                           # 身份与访问管理模块
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
│   │   ├── common/exceptions.py
│   │   ├── current_user/          #     ports.py（TokenManagerPort）/ event_handlers.py
│   │   ├── user/                  #     dto.py / services.py（UserApplicationService）/ exceptions.py
│   │   ├── resource/              #     dto.py / services.py（ResourceApplicationService）/ exceptions.py
│   │   ├── role/                  #     dto.py / services.py（RoleApplicationService）/ exceptions.py
│   │   └── user_role_assignment/  #     services.py
│   ├── infrastructure/
│   │   ├── settings.py            #   IAMSettings / JWTConfig / IAM_SETTINGS
│   │   ├── adapters/              #   端口实现：token_manager_adapter.py（骨架）
│   │   └── persistence/tortoise/  #   每实体一文件（模型 + 仓储）
│   │       ├── models/            #     __init__.py / user.py / dept.py / resource.py / permission.py / role.py / role_permission.py / role_dept.py
│   │       └── repositories/      #     __init__.py / user.py / dept.py / resource.py / permission.py / role.py（含 领域↔表 映射）
│   └── interface/
│       ├── dependences.py         #   组合根：get_*（http / bootstrap / python api 共用）
│       └── http/user/             #   api.py / schemas.py
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
  - `persistence`：`backend`（选择持久化后端）+ `auto_migrate` + `options`（后端专属，core 原样透传、不解释）
- 实体用 pydantic `BaseModel`；值对象用 `@dataclass(frozen=True)`（带 `__post_init__` 校验 + 脱敏 property）。
- **实体 ID**：`BaseEntityId`（持有 `uuid.UUID`）及其子类 `UserId`/`RoleId`/`DeptId`/`UserRoleId`/`ResourceId`/`PermissionId`/`EventId`；用 `XxxId.new()` 生成（UUIDv7）。**不设 IdProvider 端口**。
- `AuditableEntity[IdType]` 泛型审计基类（created/updated/deleted 的 at/by）。
- 仓储继承 `BaseRepository`：`get / create / bulk_create / update / hard_delete`。
- **删除语义统一**：`delete` = **软删**（实体方法，置 `status=DELETED`+`deleted_at/by`）；`hard_delete` = **物理删**（仓储）；`evict` = 缓存淘汰。**裸 `delete` 绝不表示物理删除。**
- 枚举统一 `str, Enum` 且以 `Enum` 结尾（`StatusEnum`、`UserTypeEnum`、`DataScopeEnum`）。
- 异常分 Domain / Application 两条层级；按子域拆分，common 只放跨域共用；由 `core.exceptions.global_exception_handler` 兜底（**领域/应用→HTTP 状态码的映射尚未实现**）。
- `PageResult[DataType]`（`core/utils/schemas.py`）；`check_unique` / `check_data_scope`（`core/utils/validators.py`）。
- interface/schemas 可直接引用 domain 值对象作字段类型（pydantic 自动走 `__post_init__`）。
- 应用服务接 DTO（`CreateUserIn` 等）并调用领域服务完成业务逻辑。
- **事务**：`TransactionContext` + `InTransactionType`（DI）；实现由持久化后端提供，经 `core.infrastructure.persistence.get_in_transaction()` 取用；应用层 `async with in_transaction():`（tortoise 事务连接按 task ContextVar 自动绑定）。
- **领域事件**：`EventBus` / `EventHandler` 抽象，`BaseEvent` 在 `core/domain/events.py`。
- **持久化（后端中立）**：只有 `infrastructure/persistence/` 内允许 import 具体 ORM；core 只通过门面访问。
  - 抽象层：`core/infrastructure/persistence/__init__.py`（`start/stop_persistence`、`get_in_transaction`）
  - 具体后端：`core/infrastructure/persistence/{backend}/{backend}_backend.py`
  - 模型路径约定：`app.{模块}.infrastructure.persistence.{backend}.models`（**拆包后必须在 `models/__init__.py` 汇总导出**，否则 Tortoise 发现不到模型）
  - 迁移：aerich，`migrations/` **不入库**（版本账本在数据库 `aerich` 表）；`auto_migrate` 控制启动期是否迁移
- **模块 bootstrap**：`core.start()` 按 `core.modules` 动态 import `app.{模块}.bootstrap` 并调用其 `bootstrap()`（钩子可选）。core 只认约定，不认识具体模块。
  - **资源/权限目录声明固定放各模块自己的 `bootstrap.py`**（如 `IAM_RESOURCE_DECLARATIONS`），启动时幂等注册；不塞进包 `__init__`，也不散落在子包里。
- **组合根**：`app/{模块}/interface/dependences.py` 提供 `get_*`，由 http（FastAPI `Depends`）、bootstrap、python api 共用。
- **抽象取舍判据**：Port 只在「**触碰外部（IO/第三方）**」或「**测试要替换**」时才抽；纯计算/纯数据**不抽**（直接函数/值对象）。
- **包 `__init__` 不放重副作用**：模块启动钩子独立成 `bootstrap.py`、FastAPI app 用工厂而非模块级实例。
- **领域规则收口在实体**（防漂移）：如 `User` 的 nickname 缺省=username、非超管不得使用保留用户名（`admin`）。
- **资源/权限目录（iam RBAC）**：资源=名词（`module` 分组、扁平无层级），权限=资源×操作；权限标识 `module:resource:action`（如 `iam:user:create`），完整 key 运行时派生、不落库；`(module,code)` 与 `(resource_id,action)` 唯一。
- **角色（iam）**：`code` 为唯一标识（不可改），`name` 仅作昵称。角色聚合跨三表：`iam_role` + 关系表 `iam_role_permission` / `iam_role_dept`（**裸映射：无 status/审计，移除即物理删**）。**聚合根 `Role` 持有 `permission_ids` / `custom_dept_ids`（其他聚合的 id 引用，非对象）**，由 `RoleRepository` 整体装配/保存（`get`/`get_all` 连带集合，`create`/`update` 连带落库，关系做差集替换）；**跨聚合不级联**，一致性靠读路径按 ACTIVE 过滤。`user_role` 才是实体（因需用户自助 DISABLED 某条授权；时限也挂它）。

### 命名约定

- **自定义 / 第三方依赖的抽象**：接口用 `XxxPort`（`ports.py`），实现用 `XxxAdapter`（`adapters/xxx_adapter.py`）——对应六边形 Port/Adapter。
- **DDD 原生抽象**（`Repository` / `EventBus` / `UnitOfWork`）：沿用 DDD 词汇命名接口，实现以 `XxxImpl` 结尾（如 `EventBusMemoryImpl`、`UserRepositoryTortoiseImpl`）。
- **纯计算工具**：直接放 `core/utils/`（函数或简单类，如 `password_hash`、`JWTUtil`），**不套 Port**。
- 枚举统一 `XxxEnum`，且 `str, Enum`。

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
