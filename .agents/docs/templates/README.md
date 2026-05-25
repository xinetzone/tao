# Templates: 复用骨架库

本目录存储 AgentForge 中供开发者与 AI 复用的标准化模板。

## 模板清单

| 模板 | 用途 | 何时使用 |
|-----|------|---------|
| [`agent-memory-entry-template.md`](./agent-memory-entry-template.md) | 记忆条目 | 从复盘中提取长期可复用知识时 |
| [`agent-dream-session-template.md`](./agent-dream-session-template.md) | 做梦会话 | 需要对多条记忆进行重组、发现洞见时 |

## 使用指南

1. 记忆条目：按模板字段逐项填写，存入 `../superpowers/memories/`
2. 做梦会话：当 memories/ 下累积 3+ 条相关记忆时，触发做梦重组

详见 [`../references/agent-memory-dream-protocol.md`](../references/agent-memory-dream-protocol.md)。
