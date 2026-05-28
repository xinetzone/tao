# Roles

本目录承载协作元模型中的 `Role` 实例，用于定义职责模板、默认规则绑定、权限边界和协作期望。

## 目录边界

- 不存放执行日志
- 不存放临时上下文
- 不直接复制 `skills/` 内容
- 每个角色文件保持声明式语义，不堆叠长篇自由提示词

## 角色文件约定

每个角色文件使用 `+++` 分隔符包裹 TOML 前置元数据（frontmatter），下方为 Markdown 描述正文。

### Frontmatter 字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 角色唯一标识（kebab-case），必须与文件名一致 |
| `domain` | string | 是 | 所属领域 |
| `bindings.rules` | array | 否 | 默认绑定的规则路径列表（相对 `.agents/`） |
| `bindings.references` | array | 否 | 默认绑定的参考文档路径列表 |
| `bindings.skills` | array | 否 | 默认绑定的技能 id 列表 |
| `permissions.can_modify` | array | 否 | 可修改的文件 glob 列表 |
| `permissions.cannot_modify` | array | 否 | 禁止修改的文件 glob 列表 |

Markdown body 保留三个节：Description、Responsibilities、Non-Goals。

### Frontmatter 与 body 的职责分界

- **frontmatter** = 机器可解析的声明（`id`、`domain`、`bindings`、`permissions`），供运行时路由和校验工具消费
- **Markdown body** = 人类可读的描述（Description、Responsibilities、Non-Goals），供评审和文档使用
- JSON Schema 校验定义见 `.agents/schemas/role.schema.json`

## 当前角色清单

| 文件 | 角色 | 领域 | 状态 |
|---|---|---|---|
| `collaboration-architect.md` | Collaboration Architect | governance+knowledge | 已审查 |
| `execution-orchestrator.md` | Execution Orchestrator | execution | 已审查 |
| `governance-auditor.md` | Governance Auditor | governance | 已审查 |
| `organization-steward.md` | Organization Steward | organization | 已审查 |
| `python-dev.md` | Python Dev | engineering | 占位 |
| `full-stack.md` | Full Stack | engineering | 占位 |
| `frontend-dev.md` | Frontend Dev | engineering | 占位 |
| `backend-dev.md` | Backend Dev | engineering | 占位 |
| `devops.md` | DevOps | infrastructure | 占位 |
| `reviewer.md` | Reviewer | governance | 占位 |

## 审查流程

新增角色须通过 `.agents/workflows/role-review.md` 定义的四道门禁审批。提案模板见 `.agents/workflows/role-review/templates/proposal.md`。

当前四个角色已通过试运行自审查，审查记录见 `.agents/workflows/role-review/verification/`。
