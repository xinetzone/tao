# 19. 三大流派与条件加载范式

## 19.1 三大流派对比

| 维度 | AGENTS.md 标准（开放） | CLAUDE.md+.claude/（Anthropic） | AGENTS.md+.agents/（AgentForge） |
|------|----------------------|-------------------------------|--------------------------------|
| 定位 | "AI 的 README" | Claude Code 项目配置 | "AI 智能体的世界" |
| 入口 | AGENTS.md（扁平） | CLAUDE.md（<200行路由） | AGENTS.md（路由契约+Mermaid） |
| 规则 | 全部写入口 | .claude/rules/+paths:glob | .agents/rules/+任务路由表 |
| 技能 | 不涉及 | .claude/skills/+SKILL.md | .agents/skills/+SKILL.md+评测 |
| 子智能体 | 不涉及 | .claude/agents/+工具白名单 | .agents/roles/+teams/+协作元模型 |
| 声明式配置 | 无 | settings.json（权限/hooks） | world.toml（kernel/fragments/capabilities/memory） |
| 条件加载 | 嵌套 AGENTS.md | paths: frontmatter glob | 任务类型→规范入口路由表 |
| 记忆 | 不涉及 | agent-memory/（自动 MEMORY.md） | docs/superpowers/memories/（模板+做梦协议） |
| 支持方 | OpenAI/Google/Cursor/30+ | 仅 Claude Code | 自研 |

## 19.2 条件加载的两种范式

| 范式 | 代表 | 机制 | 优势 | 劣势 |
|------|------|------|------|------|
| Glob 匹配 | Claude Code | `paths: ["src/api/**/*.ts"]` | 无需中央路由、自动触发 | 仅按文件路径 |
| 路由表 | AgentForge | 任务类型→必读入口映射 | 可按语义路由 | 依赖AI主动读取 |

**两者不互斥**：glob 适合 IDE 集成自动注入，路由表适合 CLI/对话式按需加载，理想状态下可并存。
