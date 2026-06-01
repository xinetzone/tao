# 跨工具目录桥接

本文档说明 `.agents/` 目录与主流 AI 工具目录之间的语义映射关系，便于不同工具桥接消费。

## 目录映射表

| `.agents/` | `.claude/` (Claude Code) | `.github/` (Copilot) | 语义 |
|---|---|---|---|
| `rules/` | `rules/` | `agents/` | 领域规则，支持 `paths:` glob 条件加载 |
| `skills/` | `skills/` | — | 技能资产，SKILL.md 含 YAML frontmatter |
| `docs/` | — | — | AI 专属知识库 |
| `workflows/` | `commands/` | `workflows/` | 流程化任务说明 |
| `roles/` | `agents/` | — | 角色声明（TOML + Markdown 双格式） |
| `templates/` | — | — | 标准化模板文件 |
| `scripts/` | — | — | 自动化校验/执行脚本 |

## 规则条件加载

规则文件支持 `paths:` YAML frontmatter 实现 glob 条件加载，与 Claude Code `.claude/rules/` 的条件加载机制对齐。示例：

```yaml
---
paths:
  - "**/*.py"
  - "pyproject.toml"
  - "uv.lock"
---
```

当 agent 在匹配路径的文件上工作时，对应规则才会被加载，从而节省上下文。
