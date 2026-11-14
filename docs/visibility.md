# 用户侧内容可见性（推荐模式）

> 状态：**推荐模式**，不是平台强制抽象。枚举取值、默认值、共享关系由各模块自持；平台只提供 iam 原语与边界约束。
> 参考实现：`orange-tools` 仓的 `tools` 模块。

## 1. 三个正交维度

| 维度 | 回答的问题 | 载体 | 作用面 |
|---|---|---|---|
| 功能权限码 | 能不能使用这个功能 | 角色 → `CurrentUser.permission_codes` | 接口 / 页面入口 |
| 管理侧 `data_scope` | 在管理面能治理哪些行 | 角色 → `CurrentUser.data_scope_spec` | 管理侧行过滤 |
| 用户侧 `visibility` | 我创建的内容给谁看 | 内容行的 `visibility` 字段 | 用户侧读过滤 |

三者不能互相替代：

- 有功能码不等于能看某一行；
- 有 `data_scope` 不等于能看用户侧私密内容；
- 有 `visibility` 不等于能修改内容，写操作仍只认 owner。

**不要**把 `data_scope` 与 `visibility` OR 进同一条读路径。这会让 `self` 对管理者失效，或者让用户在业务页意外看到不该看的内容。

## 2. 内容模型

内容行至少需要：

- `created_by`：创建者（owner）；
- `dept_id`：创建时的部门快照，供部门类可见性判定；
- `visibility`：独立枚举。

参考取值（模块可按业务扩展）：

```text
self            仅创建者
dept            创建时的同部门成员
dept_and_child  创建时部门及其所有子部门
public          所有已登录用户
```

约定：

- 新建默认 `self`；
- 部门类可见性按**创建时的部门快照**判定，避免用户换部门后历史内容归属漂移；
- `public` 指已登录用户，不是匿名公开；
- 不要复用 iam 的 `DataScopeEnum`——两者语义不同。

## 3. 读 / 写边界

用户侧读：

```text
owner
∨ visibility = public
∨ (visibility = dept           ∧ task.dept_id = viewer.dept_id)
∨ (visibility = dept_and_child ∧ task.dept_id ∈ viewer.dept_chain)
```

其中：

```text
viewer.dept_chain = { viewer.dept_id } ∪ viewer.dept_ancestors
```

即：任务创建部门是查看者所在部门**或其祖先**时可见。

写入边界：

- 改信息、执行、增删材料、删除 / 恢复：**只认 owner**；
- `visibility` 只决定读，不授予写权限；
- 管理侧的治理动作走独立权限码 + `data_scope`，不要复用 owner 规则。

## 4. 用户侧列表

列表查询必须把可见性条件下推到 SQL，分页和 count 使用同一条件，不能只在内存/前端过滤。

推荐视图：

- **我的任务**：`created_by = viewer`；
- **部门与公开**：按可见性过滤后的内容。

「部门与公开」是否包含自己创建的任务，是一个产品选择：

- 推荐：只排除自己创建的 `self` 私有任务，保留自己共享到 `dept / dept_and_child / public` 的任务。这样两个 Tab 一个按归属、一个按可见范围，语义正确；自己的共享任务在两边都出现是合理的。
- 如果要求两个 Tab 完全不重叠，则排除全部 `created_by = viewer`，并把 Tab 改名为「共享给我 / 他人共享」，避免名字与过滤条件不一致。

列表状态（Tab、页码、筛选、回收站）放 URL；跳详情时把列表 URL 放进 `location.state.from`，详情返回时恢复，避免每次都回到第一页。

## 5. 管理侧

管理侧与用户侧是**两组独立入口**，不要用同一个端点加 `as_admin` / `scope=all` 之类的开关切换行策略。

- 独立权限码：`manage_read`、`manage_restore`、`manage_hard_delete` 等；
- 行范围：`data_scope`，不读 `visibility`；
- 认证来源：仅交互式会话（API Key 不可执行管理动作）；
- 治理写动作：写审计（恢复 / 彻底删除等）。

管理侧在 `data_scope` 范围内可以看到 `visibility=self` 的内容；这是治理语义，不是用户侧读取。用户侧的可见性只约束业务入口。

管理列表建议展示创建人和所属部门，且部门对所有可见性都显示（包括 `public`）；用户侧为了隐私或界面简洁，可以用「公开」替代部门。

## 6. iam 提供的原语

### 部门祖先链

`CurrentUser.dept` 是部门快照：

```python
DeptSummary(
    id=...,
    name=...,
    ancestors=(...),   # 根 → 父，不含自己
)
```

`dept_and_child` 判定直接使用 `{dept.id, *dept.ancestors}`，不需要每次请求查部门树。

快照失效：

- 用户换部门 → `UserChanged` 清快照；
- 部门移动 → 被移动部门及其子树用户的祖先链变化，需要清快照；
- 部门重命名 → `dept.name` 进了快照，也需要清该部门用户快照；
- 旧快照结构不兼容时按缓存未命中重建。

### 批量展示引用

跨模块展示创建人 / 部门时，走 iam 公开 Python API：

```python
get_user_refs(user_ids)   # id / username / nickname / avatar_url
get_dept_refs(dept_ids)   # id / name
```

- 按页收集去重 ID，一次批量查询；**不要**在循环里逐条查，避免 N+1；
- 包含软删用户 / 部门，避免历史内容显示空白；
- 只在需要展示的视图调用，例如「部门与公开」或管理列表；
- 解析失败时降级为不含引用信息并记日志，不要让列表整体失败；
- 调用点放在**消费方的 infrastructure adapter**，不要在 application/domain 直接 import 其他模块。

## 7. 性能

- 每页固定多 1 次用户 `id IN (...)` + 1 次部门 `id IN (...)`，不是每行一次；
- 头像由浏览器加载并缓存，URL 带版本号，同一 owner 复用；
- 页面大小 10–100 时，额外开销可以忽略；
- 如果某个视图不需要创建人/部门，就不要调用引用 API。

## 8. 参考实现（tools）

后端：

- `app/tools/domain/task/enums.py`：`TaskVisibilityEnum`
- `app/tools/domain/task/services.py`：`TaskAccessService.can_view / can_edit / can_govern`
- `app/tools/infrastructure/persistence/tortoise/postgres/repositories/task.py`：
  `_visible_filter` / `get_all_visible` / `count_visible`
- `app/tools/application/task/services.py`：`get_page` 的 `shared_only` 过滤与 owner/dept 装配
- `app/tools/application/task_management/services.py`：管理侧 `data_scope` + `manage_*`
- `app/tools/infrastructure/adapters/directory_adapter.py`：iam 批量引用防腐层

前端：

- `web/src/features/tools/tasks/TaskListPage.tsx`：我的 / 部门与公开、列表状态
- `web/src/features/tools/components/desktop/TaskTable.tsx`
- `web/src/features/tools/components/mobile/TaskCardList.tsx`
- `web/src/features/tools/manage/TaskManageListPage.tsx`
- `web/src/features/tools/manage/TaskManageDetailPage.tsx`

注意：tools 的默认值、`shared_only` 语义、部门快照策略都是参考选择，不是平台强制规定。

## 9. 反模式

- 把 `data_scope` 和 `visibility` 做 OR 合并；
- 复用 `DataScopeEnum` 表达内容可见性；
- 同一个用户端点用查询参数切换管理 / 用户行策略；
- 只在列表内存里过滤，分页 count 仍按全量；
- 循环内逐条调用用户 / 部门查询；
- 把 `visibility` 放进 `core` 或 `iam`，强迫所有模块用同一套业务语义；
- 管理侧隐式绕过 `visibility` 却不审计。

## 10. 可扩展方向

- `group` / 显式共享关系 / 审批流；
- 可见性变更后的读取缓存失效策略；
- 部门归属按“创建时快照”还是“当前部门”，由模块按业务选择；
- 可见性筛选与管理筛选的索引设计（例如 `(visibility, dept_id)`）。
