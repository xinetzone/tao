# 第 3 章 · 执行过程

### 3.1 Phase 1: 协作元模型定义

**时间线**：
1. Brainstorming (6 轮) → 收窄为"双层结构 + 5 域 15 实体"
2. 产出 design spec → 用户逐段认可
3. 产出 implementation plan
4. 产出稳定参考页 `agent-collaboration-metamodel.md`
5. 更新 `AGENTS.md` 和 `.agents/README.md` 导航

**关键产出**：

| 文件 | 定位 |
|---|---|
| `agent-collaboration-metamodel-design.md` | 设计 spec，含语义内核收敛过程 + 后续演进建议 |
| `agent-collaboration-metamodel.md` | 8 章稳定参考页，两层结构 + 5 域 15 实体 + 关键关系 + 约束 |
| `AGENTS.md` | 新增第 3 节"协作元模型"，含 Mermaid 图 + 核心事实 + 路由 |
| `.agents/README.md` | 新增"语义目录演进"节 |

**核心设计决策**：

```
双层结构：
  MetaModel Layer (是什么)  → 实体、关系、状态语义
  Governance Layer (怎么做)  → 约束、职责边界、审计规则

五大领域：
  Organization → Team, Role, Agent
  Execution    → Mission, Task, Workflow, Handoff
  Knowledge    → Memory, Context, Rule, Skill, Artifact
  Governance   → Policy, Permission
  Runtime      → Session

五大强约束：
  1. Agent 不能脱离 Role 进入协作
  2. Task 必须归属 Mission
  3. Workflow 不拥有知识
  4. Permission 赋给 Role/Agent，不直接赋 Task
  5. Handoff 必须是显式对象
```

### 3.2 Phase 2: roles/ 语义目录

**时间线**：
1. 用户提出"可以考虑添加 roles 等目录"
2. AI 提出三个候选选项，用户选择 `.agents/roles/` 为第一批试点
3. AI 设计 4 个角色覆盖五大领域
4. 创建 4 个角色文件 + roles/README.md

**关键产出**：

| 角色 | 领域 | 核心职责 |
|---|---|---|
| `organization-steward` | Organization | 维护 Team/Role/Agent 组织边界与归属关系 |
| `execution-orchestrator` | Execution | 编排 Mission/Task/Workflow/Handoff |
| `collaboration-architect` | Governance + Knowledge | 维护元模型语义边界与目录映射 |
| `governance-auditor` | Governance | Policy/Permission 治理约束与审计 |

**设计约束**：

- 每个角色使用四字段模板：Role Identity / Responsibilities / Default Bindings / Non-Goals
- Responsibilities 使用编排性动词（设计/维护/审核/规范），避免运行时动词（执行/实现/调用）
- Default Bindings 中引用路径须真实存在
- 角色名不与元模型实体名（Team/Agent 等）重复

### 3.3 Phase 3: Role Review 工作流 + 试运行

**时间线**：
1. Brainstorming → 选择"新角色引入审批流"
2. 用户认可方案 A：顺序门禁模型 (4 Gate)
3. 用户认可第二部分：提案模板 + 试运行方案
4. 用户认可第三部分：产物清单 + 命名 + 非目标
5. 用户认可 spec review
6. 选择 Subagent-Driven 执行方式（1）
7. AI 并行/串行派发 5 个 Task，全部完成

**关键产出**：

```
.agents/workflows/
├── role-review.md                              # 工作流主文档
└── role-review/
    ├── templates/
    │   └── proposal.md                         # 角色提案模板
    └── verification/
        ├── gate-01-organization-steward.md
        ├── gate-02-execution-orchestrator.md
        ├── gate-03-collaboration-architect.md
        └── gate-04-governance-auditor.md
```

**四道门禁标准**：

| Gate | 审查人 | 焦点 | 检查项数 |
|---|---|---|---|
| Gate 1 | Organization Steward | 组织归属 | 3 (Domain/命名/唯一性) |
| Gate 2 | Execution Orchestrator | 执行影响 | 3 (编排性/Agent边界/运行时排除) |
| Gate 3 | Collaboration Architect | 语义一致性 | 3 (字段完整性/引用有效性/映射兼容性) |
| Gate 4 | Governance Auditor | 合规审计 | 3 (强约束/越界/可追踪性) |

**试运行结果**：4 Gate 全部 ✅ 通过，验证了元模型的自指一致性。

**Handoff 协议**：

```
Gate N → Gate N+1
来源角色: [审查者]
目标角色: [下一审查者]
交接内容: 审查结论 + 未解决问题
状态: prepared → accepted → rejected
```

### 3.4 Phase 4: teams/ 语义目录

**时间线**：
1. 用户"继续" → 选择 teams/ 目录方向
2. 一轮 brainstorming 收敛：六字段模板 + 1 个核心 Team + 复用 Role Review
3. 用户认可方案 → 全部 8 个操作并行执行
4. 验收通过

**关键产出**：

| 操作 | 文件 | 说明 |
|---|---|---|
| 🆕 | `.agents/teams/README.md` | 目录说明页，六字段约定 + 审查流程 |
| 🆕 | `.agents/teams/core-governance.md` | 核心 Team 实例，含 4 个 Role |
| 🆕 | `.agents/workflows/role-review/templates/team-proposal.md` | Team 提案模板 |
| ✏️ | `AGENTS.md` | Mermaid 图 + 核心事实 + 路由表同步 |
| ✏️ | `.agents/README.md` | teams/ 从"后续评估"→"现有目录" |
| ✏️ | `agent-collaboration-metamodel.md` | 目录映射新增 teams/，演进更新 |
| ✏️ | `.agents/workflows/role-review.md` | 新增第 9 节"Team 审查扩展" |

**六字段模板**（在 Role 四字段基础上追加）：

| # | 字段 | 说明 |
|---|---|---|
| 1 | Team Identity | Name / Domain / Description |
| 2 | Responsibilities | Team 级治理职责 |
| 3 | **Member Roles** | ✨ 显式表格 + 绑定原因 |
| 4 | **Cross-Team Policy** | ✨ 跨 Team 协作策略 |
| 5 | Default Bindings | Rules / References / Skills |
| 6 | Non-Goals | 明确排除范围 |
