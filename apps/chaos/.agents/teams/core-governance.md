# Core Governance

## Team Identity

- **Name**: `core-governance`
- **Domain**: Organization
- **Description**: AgentForge 核心治理团队，作为唯一治理容器承载当前所有角色，覆盖五大领域协作语义。

## Responsibilities

- 定义并维护 AgentForge 项目的治理边界与组织容器语义
- 审核并批准新 Role 的引入，确保角色与 Team 治理边界一致
- 承载 Policy 与 Permission 的默认治理策略
- 在多 Team 场景下定义跨 Team 协作的 Handoff 协议
- 维护 Team 级 Memory，确保组织知识的长期可追溯性

## Member Roles

| Role | 绑定原因 |
|---|---|
| [`organization-steward`](../roles/organization-steward.md) | Organization 域，维护 Team/Role/Agent 组织边界 |
| [`execution-orchestrator`](../roles/execution-orchestrator.md) | Execution 域，编排 Mission/Task/Workflow/Handoff |
| [`collaboration-architect`](../roles/collaboration-architect.md) | Governance + Knowledge 域，维护元模型语义边界与目录映射 |
| [`governance-auditor`](../roles/governance-auditor.md) | Governance 域，Policy/Permission 治理约束与审计 |

## Cross-Team Policy

当前为单 Team 模式。`core-governance` 是 AgentForge 项目的唯一治理容器，承载全部现有角色。

欢迎后续引入子团队（如 `delivery-team`、`knowledge-team`），届时本声明将更新为跨 Team 协作策略，包含显式 Handoff 协议与治理边界划分。

## Default Bindings

### Rules

- `.agents/rules/documentation.md`
- `.agents/rules/skills.md`

### References

- `.agents/docs/references/agent-collaboration-metamodel.md`

### Skills

- `brainstorming`

## Non-Goals

- 不替代单个 Role 的职责定义与审查（Role 审查走独立工作流）
- 不直接执行任务或编排工作流（属于 Execution 域）
- 不定义具体业务实现细节
