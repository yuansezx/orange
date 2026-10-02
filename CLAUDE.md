# Orange 项目指南

## 项目概述
基于 FastAPI 的 DDD 分层项目，采用四层架构（domain → application → infrastructure → interface）。

当前仅有一个业务模块：**iam**（Identity and Access Management，身份与访问管理）。

## 技术栈
- Python 3.13+
- FastAPI（生命周期管理 + 全局异常处理）
- pydantic / pydantic-settings（分节 YAML（core / iam）+ .env 配置，`YamlConfigSettingsSource`）
- loguru（异步日志，分级输出到文件）
- future-uuid（UUIDv7 生成）
- pyjwt（JWT 签发与校验）、redis（redis-py 异步客户端，用于令牌存储）
- 包管理: uv

## 项目结构
```
app/
├── __init__.py                    # FastAPI 应用工厂 create_app() + lifespan
├── core/                          # 全局共享基础设施
│   ├── __init__.py                # init_logger() 日志初始化 + get_event_bus() + start()
│   ├── domain/                    # DDD 领域抽象（无业务语义）
│   │   ├── entities.py            #   AuditableEntity[IdType] 审计基类（泛型，含软删除字段）
│   │   ├── events.py              #   BaseEvent 领域事件基类
│   │   ├── event_bus.py           #   EventBus, EventHandler 抽象
│   │   ├── ports.py               #   IdProviderPort[IdType], EventIdProvider
│   │   ├── repositories.py        #   BaseRepository[IdType, EntityType] 仓储接口基类
│   │   ├── units_of_work.py       #   TransactionContext, InTransactionType
│   │   └── value_objects.py       #   BaseEntityId, EventId（@dataclass frozen，字段 value: str）
│   ├── infrastructure/
│   │   ├── settings.py            #   AppBaseSettings / CoreSettings / CORE_SETTINGS
│   │   ├── event_bus_impl.py      #   EventBusMemoryImpl（DDD 原生抽象 → Impl 命名）
│   │   └── adapters/
│   │       └── id_provider_adapter.py  # EventIdProviderUUID7Adapter（端口实现 → Adapter 命名）
│   ├── interface/
│   │   └── dependences.py         #   get_event_id_provider()
│   ├── exceptions.py              #   global_exception_handler + DomainBaseException/ApplicationBaseException
│   └── utils/
│       ├── schemas.py             #   PageResult[DataType] 通用分页结果
│       ├── validators.py          #   check_unique, check_data_scope 通用工具
│       ├── type_utils.py          #   to_set
│       └── jwt_util.py            #   JWTUtil（encode/decode，基于 pyjwt）
├── iam/                           # 身份与访问管理模块
│   ├── domain/                    # 领域层
│   │   ├── shared/                #   共享值对象、枚举、异常
│   │   │   ├── enums.py           #     StatusEnum(ACTIVE/DISABLED/DELETED, str Enum)
│   │   │   ├── value_objects.py   #     Phone, Email（校验 + masked）, UserId, RoleId, DeptId, UserRoleId
│   │   │   └── exceptions.py      #     IAMDomainBaseException
│   │   ├── user/                  #   用户子域
│   │   │   ├── entities.py        #     User(AuditableEntity[UserId])，含 can_update/can_delete
│   │   │   ├── enums.py           #     UserTypeEnum(str Enum，含 SUPER_ADMIN/SYSTEM)
│   │   │   ├── ports.py           #     PasswordHasherPort, UserIdProviderPort（领域端口）
│   │   │   ├── repositories.py    #     UserRepository, SearchUser
│   │   │   ├── services.py        #     CheckUserUniqueService, UserAccessService
│   │   │   └── exceptions.py      #     PasswordPolicyViolationException 等
│   │   ├── role/                  #   角色子域
│   │   │   ├── entities.py        #     Role(AuditableEntity), RoleFilter
│   │   │   ├── enums.py           #     DataScopeEnum(str Enum)
│   │   │   ├── ports.py           #     RoleIdProviderPort
│   │   │   ├── repositories.py    #     RoleRepository
│   │   │   └── services.py        #     RoleAccessService（数据权限校验）
│   │   ├── dept/                  #   部门子域
│   │   │   ├── entities.py        #     Dept(AuditableEntity)
│   │   │   ├── ports.py           #     DeptIdProviderPort
│   │   │   ├── repositories.py    #     DeptRepository
│   │   │   └── services.py        #     DeptAccessService（数据权限校验）
│   │   ├── user_role_assignment/  #   用户-角色分配子域
│   │   │   ├── entities.py        #     UserRoleAssignment(AuditableEntity)
│   │   │   ├── ports.py           #     UserRoleIdProviderPort
│   │   │   └── repositories.py    #     UserRoleRepository
│   │   ├── login_log/             #   登录日志子域
│   │   │   └── entities.py        #     LoginLog(BaseModel)
│   │   └── current_user/          #   当前用户上下文
│   │       ├── entities.py        #     CurrentUser(BaseModel)
│   │       └── repositories.py    #     CurrentUserRepository（当前用户缓存读写）
│   ├── application/               # 应用层
│   │   ├── common/
│   │   │   └── exceptions.py      #     IAMApplicationBaseException, PermissionDeniedException,
│   │   │                          #     OperationNotAllowedException, AuthenticationException, InvalidTokenException
│   │   ├── current_user/
│   │   │   ├── ports.py           #     TokenManagerPort（令牌管理端口：authenticate/create/revoke/revoke_all）
│   │   │   └── event_handlers.py  #     clear_current_users_cache（事件处理器）
│   │   ├── user/
│   │   │   ├── dto.py             #     CreateUserIn, UpdateUserIn, GetUsersIn
│   │   │   ├── services.py        #     UserApplicationService（含 create/update）
│   │   │   └── exceptions.py      #     UserExistsException, UserNotExistException
│   │   └── user_role_assignment/
│   │       └── services.py        #     UserRoleApplicationService
│   ├── infrastructure/            # 基础设施实现
│   │   ├── settings.py            #   IAMSettings / JWTConfig / IAM_SETTINGS
│   │   └── adapters/
│   │       ├── id_provider_adapter.py    # UserIdProviderUUID7Adapter 等 UUIDv7 实现
│   │       └── token_manager_adapter.py  # TokenManagerJWTRedisAdapter（骨架，待补全）
│   └── interface/                 # 接口适配层
│       └── http/user/
│           ├── api.py             #     用户 API 路由
│           └── schemas.py         #     接口层 schema（复用 domain 值对象）
├── run.py                         # 启动入口（uvicorn）
├── pyproject.toml                 # 项目依赖
├── config_example.yaml            # 配置示例（core / iam 分节）
└── CLAUDE.md                      # 本文件
```

## 架构规范
- **DDD 四层结构**: domain → application → infrastructure → interface
- **层依赖方向**: interface → application → domain, infrastructure → domain
- **core 层不依赖任何业务模块**
- **业务模块之间平级**，允许因业务需要引用（如 order 依赖 iam 的 User）
- 配置采用 **分节 YAML（`core` / `iam`）+ .env**，通过 `yaml_config_section` 指定各自 section；优先级: dotenv > yaml > init > env > file_secret
- 实体用 `pydantic BaseModel`，值对象用 `@dataclass(frozen=True)`（带 `__post_init__` 校验 + property 脱敏方法）
- **实体 ID** 使用继承 `BaseEntityId` 的冻结 dataclass 值对象（如 `UserId`, `RoleId`, `DeptId`），通过 `IdProviderPort[IdType]` 接口生成（UUIDv7）
- 审计基类 `AuditableEntity[IdType]` 用泛型，各模块自行决定 IdType，含 deleted_at/deleted_by 软删除字段
- 仓储接口继承 `BaseRepository[IdType, EntityType](ABC)`，提供 get/create/bulk_create/update/delete 抽象方法
- 每个子域提供 `ports.py` 定义领域层抽象（如 `PasswordHasherPort`、`UserIdProviderPort`），基础设施层 `adapters/` 负责实现
- 枚举统一使用 `str, Enum`，并以 `Enum` 结尾（如 `StatusEnum`、`UserTypeEnum`），允许序列化和数据库存储
- 全局异常通过 `app.core.exceptions.global_exception_handler` 捕获，异常分 Domain 和 Application 两条层级
- 应用层异常按子域拆分（如 `app.iam.application.user.exceptions`），common 只放跨域共用异常
- 通用分页结果使用 `PageResult[DataType]`（含 computed_field total_pages），位于 `app/core/utils/schemas.py`
- 通用唯一性校验使用 `app.core.utils.validators.check_unique`，数据权限校验使用 `check_data_scope`
- **interface/schemas** 可直接引用 domain 值对象作为字段类型，pydantic 自动调用 `__post_init__` 校验
- 应用服务接收 DTO（如 `CreateUserIn`）并调用领域服务完成业务逻辑
- 事务通过 `TransactionContext`（抽象异步上下文管理器）+ `InTransactionType`（可调用别名）实现 DI，定义在 `app/core/domain/units_of_work.py`
- 领域事件经 `EventBus`/`EventHandler` 抽象分发，`BaseEvent` 定义在 `app/core/domain/events.py`
- **当前用户与令牌**: `CurrentUser`（`iam/domain/current_user`）承载登录上下文，经 `CurrentUserRepository` 缓存；令牌签发/校验由 `TokenManagerPort`（`iam/application/current_user/ports.py`）定义，`TokenManagerJWTRedisAdapter`（JWT + Redis）为当前骨架实现，`create/revoke/revoke_all` 待补全

### 命名约定
- **自定义 / 第三方依赖的抽象**：接口用 `XxxPort`（文件 `ports.py`），实现用 `XxxAdapter`（文件 `adapters/xxx_adapter.py`），对应六边形架构的 Port/Adapter
- **DDD 原生抽象**（`Repository` / `EventBus` / `UnitOfWork`）：沿用 DDD 词汇命名接口，实现以 `XxxImpl` 结尾（如 `EventBusMemoryImpl`、`UserRepositoryXxxImpl`）
- 枚举统一 `XxxEnum`，且 `str, Enum`

## 运行
```bash
uv run python run.py
```

## 命令/工具习惯
- 所有运行命令使用 `uv run python ...`，不直接用 `python`
