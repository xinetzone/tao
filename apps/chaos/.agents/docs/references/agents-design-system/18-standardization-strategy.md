# 18. 标准化战略分析

## 18.1 竞品定位对比

| 玩家 | 约定 | 状态 | 覆盖范围 |
|------|------|------|---------|
| OpenAI Codex CLI | AGENTS.md | 已开源，事实标准 | 扁平指令文件 |
| Anthropic | CLAUDE.md | Claude Code 内置 | 扁平指令+@file引用 |
| Cursor | .cursor/rules/*.mdc | 市场领先工具 | 规则文件，frontmatter条件匹配 |
| agentskills.io | SKILL.md | 开放标准 | 仅技能层 |
| AgentForge | AGENTS.md + .agents/ + world.toml | 提案阶段 | 全栈：内核到多世界继承 |

**关键事实**：`AGENTS.md` 名称已被 OpenAI Codex 占用，但 Codex 只把它当简单指令文件。AgentForge 在同名文件下装了远超 Codex 预期的内容。AGENTS.md 已被 Linux 基金会下的 Agentic AI Foundation 托管，GitHub 上 60k+ 仓库采用，30+ 工具通用读取。

## 18.2 三大标准化挑战

1. **复杂度梯度**：需满足"5分钟上手法则"，五级渐进式模型（Level 0-4）正是对此的回应。
2. **与事实标准的关系**：建议"超集兼容"策略 —— AGENTS.md 前 N 行纯 Markdown 兼容 Codex，`.agents/` 作为可选增强层。
3. **规范与实现分离**：需要独立的规范仓库、独立的参考实现、独立的验证工具。

## 18.3 标准化路线图建议

```
Phase 1: 规范冻结与分离
  ├── AgentForge Spec v1.0
  ├── AGENTS.md Level 0 兼容 Codex
  ├── world.toml 独立 RFC
  └── 独立 spec 仓库 + JSON Schema 验证

Phase 2: 参考实现与工具链
  ├── CLI：agentforge init / validate / doctor
  ├── IDE 插件：VS Code / JetBrains
  ├── CI 集成：GitHub Action
  └── apps/chaos/ 作为 reference implementation

Phase 3: 生态建设
  ├── Fragment Registry（类似 npm registry）
  ├── 官方 Fragment 集合
  ├── 与其他工具适配层
  └── 向 AI 工具厂商推广
```

## 18.4 三大战略优势

1. **技能层已对齐 agentskills.io**：在技能层无需重新发明轮子。
2. **世界层级继承是独家能力**：无竞品定义多 AGENTS.md 继承 + kernel 不可变 + 覆盖粒度控制。
3. **kernel/fragments 分层是独创性贡献**：在 AI Agent 约定领域全新。
