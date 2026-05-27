# Roles

本目录承载协作元模型中的 `Role` 实例，用于定义职责模板、默认规则绑定、权限边界和协作期望。

## 目录边界

- 不存放执行日志
- 不存放临时上下文
- 不直接复制 `skills/` 内容
- 每个角色文件保持声明式语义，不堆叠长篇自由提示词

## 角色文件约定

每个角色文件至少包含以下字段：

- **Role Identity**：角色名称与所属领域
- **Responsibilities**：核心职责边界
- **Default Bindings**：默认绑定的规则、参考页与能力资产
- **Non-Goals**：明确不属于该角色的范围

## 当前角色清单

| 文件 | 角色 | 领域 | 审查状态 |
|---|---|---|---|
| `organization-steward.md` | Organization Steward | Organization | ✅ 已审查 |
| `execution-orchestrator.md` | Execution Orchestrator | Execution | ✅ 已审查 |
| `collaboration-architect.md` | Collaboration Architect | Governance + Knowledge | ✅ 已审查 |
| `governance-auditor.md` | Governance Auditor | Governance | ✅ 已审查 |

## 审查流程

新增角色须通过 `.agents/workflows/role-review.md` 定义的四道门禁审批。提案模板见 `.agents/workflows/role-review/templates/proposal.md`。

当前四个角色已通过试运行自审查，审查记录见 `.agents/workflows/role-review/verification/`。
