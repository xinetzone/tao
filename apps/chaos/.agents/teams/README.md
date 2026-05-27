# Team 实例目录 (.agents/teams)

本目录承载协作元模型中 `Team` 实体的语义实例，用于定义治理边界、角色成员关系与跨 Team 协作策略。

## 目录边界

- 本目录**不存放**执行日志、临时上下文或运行时状态
- 本目录**不存放** Role 定义（Role 在 `.agents/roles/`）
- 本目录**不替代**协作元模型参考页（见 `.agents/docs/references/agent-collaboration-metamodel.md`）

## 文件约定

每个 Team 实例文件包含以下六字段声明：

| # | 字段 | 说明 |
|---|---|---|
| 1 | **Team Identity** | Name / Domain / Description |
| 2 | **Responsibilities** | Team 级治理职责，动词开头 |
| 3 | **Member Roles** | 显式表格列出所含 Role 及绑定原因 |
| 4 | **Cross-Team Policy** | 跨 Team 协作策略声明 |
| 5 | **Default Bindings** | Rules / References / Skills 三子域 |
| 6 | **Non-Goals** | Team 明确不负责的范围 |

命名约定：文件名使用英文小写连字符，与 Name 字段一致。

## 当前清单

| 文件 | Name | 角色数 | 审查状态 |
|---|---|---|---|
| [`core-governance.md`](./core-governance.md) | `core-governance` | 4 | ✅ 已审查 |

## 审查流程

新 Team 引入复用 Role Review 工作流的四道门禁，各 Gate 检查标准做 Team 适配。详见 [`.agents/workflows/role-review.md`](../workflows/role-review.md) 第 9 节"Team 审查扩展"。

提案使用专用模板：[`../workflows/role-review/templates/team-proposal.md`](../workflows/role-review/templates/team-proposal.md)。
