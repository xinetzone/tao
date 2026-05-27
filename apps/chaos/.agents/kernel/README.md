# Kernel 边界管理

> 修改 kernel 就是修改"物理定律"——影响所有在此世界中运行的 Agent。

## 什么是 Kernel

Kernel 是世界**不可分割的最小集合**——缺少任何一部分，世界就不成立。它定义了：

- Agent 如何行为（rules）
- Agent 如何理解世界（references）
- Agent 如何被治理（workflows + roles framework）
- 世界如何描述自己（manifest + README）

## 当前 Kernel 成员

| 类别 | 文件 | 职责 |
|------|------|------|
| 自描述 | `world.toml` | 世界声明式 manifest（递归自指） |
| 入口 | `README.md` | 世界宣言与入口路由 |
| 法则 | `rules/context-economy.md` | 上下文节省——所有 Agent 的基本行为法则 |
| 法则 | `rules/documentation.md` | 文档治理——知识组织的基本定义 |
| 法则 | `rules/skills.md` | 技能规范——能力如何被创建与消费 |
| 参考 | `docs/references/dao-tech-foundation.md` | 哲学-工程映射第一性原理 |
| 参考 | `docs/references/agent-collaboration-metamodel.md` | 多 Agent 协作语义 |
| 参考 | `docs/references/agent-memory-dream-protocol.md` | 认知循环协议 |
| 治理 | `workflows/role-review.md` | 角色审查——保护 kernel 边界 |
| 框架 | `roles/README.md` | 角色系统语义定义 |

## 准入标准

文件升入 kernel 必须满足**全部**条件：

1. **不可或缺性**——移除后世界丧失基本运行能力
2. **普适性**——所有 Agent（无论领域）都必须遵循
3. **稳定性**——变更频率极低，每次变更等同于"修改物理定律"

## 退出标准

文件降出 kernel 的条件（满足**任一**即可）：

1. 仅特定领域的 Agent 需要遵循
2. 移除后世界仍能基本运行
3. 变更频率较高且不影响其他 Agent

## 变更流程

1. **提议**：说明为什么需要修改 kernel
2. **影响评估**：列出所有受影响的 Agent 行为
3. **版本升级**：修改 kernel 必须升级 `world.toml` 中的 `world.version`（至少 minor）
4. **同步更新**：更新本文件的成员表

## 与 world.toml 的关系

本目录是 `[kernel.meta].boundary-policy` 的实现——它不包含 kernel 文件本身（那些文件留在原位），而是提供 kernel 的**管理元数据**。
