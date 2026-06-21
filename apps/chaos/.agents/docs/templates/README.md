# Templates: 复用骨架库

本目录存储 AgentForge 中供开发者与 AI 复用的标准化模板。

## 模板清单

### AI 记忆与学习

| 模板 | 用途 | 何时使用 |
|-----|------|---------|
| [`agent-memory-entry-template.md`](./agent-memory-entry-template.md) | 记忆条目 | 从复盘中提取长期可复用知识时 |
| [`agent-dream-session-template.md`](./agent-dream-session-template.md) | 做梦会话 | 需要对多条记忆进行重组、发现洞见时 |

### EU AI Act 合规

| 模板 | 用途 | 何时使用 |
|-----|------|---------|
| [`eu-ai-act-agents-md-template.md`](./eu-ai-act-agents-md-template.md) | AGENTS.md 合规模板 | 项目需要 EU AI Act 合规声明时 |
| [`eu-ai-act-constraints-template.toml`](./eu-ai-act-constraints-template.toml) | constraints.toml 约束模板 | 定义高风险操作与审批流程时 |
| [`eu-ai-act-role-template.toml`](./eu-ai-act-role-template.toml) | 角色定义模板 | 定义 AI 角色权限与自主级别时 |
| [`eu-ai-act-compliance-workflow-template.yml`](./eu-ai-act-compliance-workflow-template.yml) | CI 合规检查工作流 | 自动化合规扫描与门禁时 |
| [`eu-ai-act-compliance-deployment-guide.md`](./eu-ai-act-compliance-deployment-guide.md) | 部署文档 | 完整部署指南与故障排查 |

## 使用指南

### AI 记忆与学习

1. 记忆条目：按模板字段逐项填写，存入 `../superpowers/memories/`
2. 做梦会话：当 memories/ 下累积 3+ 条相关记忆时，触发做梦重组

详见 [`../references/agent-memory-dream-protocol.md`](../references/agent-memory-dream-protocol.md)。

### EU AI Act 合规

1. **AGENTS.md**: 复制 `eu-ai-act-agents-md-template.md` 到项目根目录，填写项目信息
2. **constraints.toml**: 复制 `eu-ai-act-constraints-template.toml` 到 `.agents/`，定义约束
3. **角色定义**: 复制 `eu-ai-act-role-template.toml` 到 `.agents/roles/`，定义角色权限
4. **CI 工作流**: 复制 `eu-ai-act-compliance-workflow-template.yml` 到 `.github/workflows/`，配置自动化扫描

完整实施路线见 [`../../docs/tech/agents-md-implementation-roadmap.md`](../../docs/tech/agents-md-implementation-roadmap.md)。
