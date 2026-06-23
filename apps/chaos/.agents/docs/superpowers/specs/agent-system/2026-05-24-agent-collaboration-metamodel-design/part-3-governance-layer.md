# 治理层（Governance Layer）

> 本单元涵盖原文件的 Constraints、State Semantics 章节，定义协作元模型中的强约束、弱约束与最小状态语义。

## Constraints

### Hard Constraints

- `Agent` 不能脱离 `Role` 直接进入规范性协作体系
- `Task` 必须归属于某个 `Mission` 或更高层目标容器
- `Workflow` 不拥有知识，只编排执行；知识通过 `Context`、`Rule`、`Memory`、`Skill` 注入
- `Permission` 不直接赋给 `Task`，而应赋给 `Role` 或 `Agent`
- `Handoff` 必须是显式对象，至少包含来源、目标、交接内容和状态

### Soft Constraints

- `Team` 是否必须拥有多个 `Role` 可由具体项目裁剪
- `Agent` 是否允许跨 `Team` 协作由治理层决定
- `Memory` 是否持久化及如何检索属于实现层
- `Skill` 是工具能力还是复合工作流单元，首版不强制限定实现形态

## State Semantics

首版仅定义最小状态语义，不绑定具体引擎实现。

### Task State

推荐最小状态集合：

- `draft`
- `ready`
- `in_progress`
- `handoff_pending`
- `blocked`
- `done`

### Handoff State

推荐最小状态集合：

- `prepared`
- `offered`
- `accepted`
- `rejected`
- `completed`

### Session State

推荐最小状态语义：

- 标识当前协作上下文
- 追踪参与主体、当前任务、活动角色和上下文工作集
- 为未来事件流、快照恢复和审计回放预留接口
