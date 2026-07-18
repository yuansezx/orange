# Orange 项目指南

## 项目概述
基于 FastAPI 的 DDD 分层项目，采用四层架构（domain → application → infrastructure → interface）。

当前仅有一个业务模块：**iam**（Identity and Access Management，身份与访问管理）。

## 技术栈
- Python 3.13+
- FastAPI（生命周期管理 + 全局异常处理）
- pydantic / pydantic-settings（扁平 YAML + .env 配置，`YamlConfigSettingsSource`）
- loguru（异步日志，分级输出到文件）
- future-uuid（UUIDv7 生成）
- 包管理: uv

## 项目结构
```
app/
├── core/                          # 全局共享基础设施
│   ├── __init__.py                # 日志初始化 + 应用启动入口
│   ├── domain/                    # DDD 领域抽象（无业务语义）
│   │   ├── entities.py            #   AuditableEntity[IdType] 审计基类（泛型，含软删除字段）
│   │   ├── interfaces.py          #   IdProvider[IdType] ID 生成接口
│   │   ├── repositories.py        #   BaseRepository[IdType, EntityType] 仓储接口基类
│   │   └── value_objects.py       #   BaseEntityID（@dataclass frozen，字段 value: str）
│   ├── infrastructure/
│   │   └── settings.py            #   AppBaseSettings / CoreSettings 全局配置
│   ├── schemas.py                 # PageResult[DataType] 通用分页结果
│   ├── exceptions.py              # global_exception_handler + 异常基类
│   └── utils/
│       └── validators.py          # check_unique, check_data_scope 通用工具
├── iam/                           # 身份与访问管理模块
│   ├── domain/                    # 领域层
│   │   ├── shared/                #   共享值对象、枚举、服务
│   │   │   ├── enums.py           #     Status(ACTIVE/DISABLED/DELETED, str Enum)
│   │   │   ├── value_objects.py   #     Phone, Email（校验 + masked）, UserId, RoleId, DeptId, UserRoleId
│   │   │   ├── exceptions.py      #     IAMDomainBaseException
│   │   │   ├── services.py        #     DeptAccessService, RoleAccessService（数据权限校验）
│   │   │   └── units_of_work.py   #     TransactionContext, InTransactionType
│   │   ├── user/                  #   用户子域
│   │   │   ├── entities.py        #     User(AuditableEntity[UserId])，含 can_update/can_delete
│   │   │   ├── enums.py           #     UserType(str Enum，含 SUPER_ADMIN/SYSTEM)
│   │   │   ├── ports.py           #     PasswordHasher, UserIdProvider（领域端口）
│   │   │   ├── repositories.py    #     UserRepository
│   │   │   ├── services.py        #     CheckUserUniqueService
│   │   │   └── exceptions.py      #     PasswordPolicyViolationException
│   │   ├── role/                  #   角色子域
│   │   │   ├── entities.py        #     Role(AuditableEntity), RoleFilter
│   │   │   ├── enums.py           #     DataScope(str Enum)
│   │   │   ├── interfaces.py      #     RoleIdProvider
│   │   │   └── repositories.py    #     RoleRepository
│   │   ├── dept/                  #   部门子域
│   │   │   ├── entities.py        #     Dept(AuditableEntity)
│   │   │   ├── interfaces.py      #     DeptIdProvider
│   │   │   └── repositories.py    #     DeptRepository
│   │   ├── user_role_assignment/  #   用户-角色分配子域
│   │   │   └── entities.py        #     UserRoleAssignment(AuditableEntity)
│   │   ├── login_log/             #   登录日志子域
│   │   │   └── entities.py        #     LoginLog(BaseModel)
│   │   └── current_user/          #   当前用户上下文
│   │       └── entities.py        #     CurrentUser(BaseModel)
│   ├── application/               # 应用层
│   │   ├── common/
│   │   │   └── exceptions.py      #     IAMApplicationBaseException, PermissionDeniedException
│   │   └── user/
│   │       ├── dto.py             #     CreateUserIn, UpdateUserIn
│   │       ├── services.py        #     UserApplicationService（含 create/update）
│   │       └── exceptions.py      #     UserExistsException, UserNotExistException
│   ├── interface/                 # 接口适配层
│   │   └── http/user/
│   │       ├── api.py             #     用户 API 路由
│   │       └── schemas.py         #     接口层 schema（复用 domain 值对象）
│   └── infrastructure/            # 基础设施实现
│       └── adapters/
│           └── id_provider_impl.py #     UserIdProviderUUID7Impl 等 UUIDv7 实现
├── __init__.py                    # FastAPI 应用工厂 create_app()
├── run.py                         # 启动入口（uvicorn）
├── pyproject.toml                 # 项目依赖
├── config_example.yaml            # 配置示例
└── CLAUDE.md                      # 本文件
```

## 架构规范
- **DDD 四层结构**: domain → application → infrastructure → interface
- **层依赖方向**: interface → application → domain, infrastructure → domain
- **core 层不依赖任何业务模块**
- **业务模块之间平级**，允许因业务需要引用（如 order 依赖 iam 的 User）
- 配置采用 **扁平 YAML + .env**，优先级: dotenv > yaml > init > env > file_secret
- 实体用 `pydantic BaseModel`，值对象用 `@dataclass(frozen=True)`（带 `__post_init__` 校验 + property 脱敏方法）
- **实体 ID** 使用继承 `BaseEntityID` 的冻结 dataclass 值对象（如 `UserId`, `RoleId`, `DeptId`），通过 `IdProvider[IdType]` 接口生成（UUIDv7）
- 审计基类 `AuditableEntity[IdType]` 用泛型，各模块自行决定 IdType，含 deleted_at/deleted_by 软删除字段
- 仓储接口继承 `BaseRepository[IdType, EntityType](ABC)`，提供 get/create/update/delete 抽象方法
- 每个子域提供 `ports.py` 或 `interfaces.py` 定义领域层抽象（如 `PasswordHasher`、`UserIdProvider`），基础设施层 `adapters/` 负责实现
- 枚举统一使用 `str, Enum`，允许序列化和数据库存储
- 全局异常通过 `app.core.exceptions.global_exception_handler` 捕获，异常分 Domain 和 Application 两条层级
- 应用层异常按子域拆分（如 `app.iam.application.user.exceptions`），common 只放跨域共用异常
- 通用分页结果使用 `PageResult[DataType]`（含 computed_field total_pages）
- 通用唯一性校验使用 `app.core.utils.validators.check_unique`，数据权限校验使用 `check_data_scope`
- **interface/schemas** 可直接引用 domain 值对象作为字段类型，pydantic 自动调用 `__post_init__` 校验
- 应用服务接收 DTO（如 `CreateUserIn`）并调用领域服务完成业务逻辑
- 事务通过 `TransactionContext`（抽象异步上下文管理器）+ `InTransactionType`（可调用别名）实现 DI

## 运行
```bash
uv run python run.py
```

## 命令/工具习惯
- 所有运行命令使用 `uv run python ...`，不直接用 `python`
