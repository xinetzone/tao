# 13. AGENTS.md 与 Memory / Docs 的关系

## 13.1 AGENTS.md 与 Memory

如果一个 Agent 系统有长期记忆，那么：
- `AGENTS.md` 是项目内显式、可版本控制的规则
- memory 是 Agent 系统侧的历史偏好或经验

对于工程团队来说，重要规则应该进 `AGENTS.md`，而不是只存在某个 Agent 的私有 memory。原因：可审查、可版本控制、团队共享、工具无关、更可迁移。长期记忆适合保存个人偏好；项目规范应该落盘。

## 13.2 AGENTS.md 与 docs/

| 位置 | 用途 |
|---|---|
| `README.md` | 人类快速开始 |
| `docs/` | 完整产品/架构/运维文档 |
| `AGENTS.md` | Agent 执行规则 |
| `.agents/context/` | Agent 摘要化上下文 |
| `.agents/workflows/` | Agent 任务流程 |
| `.agents/policies/` | Agent 风险约束 |
