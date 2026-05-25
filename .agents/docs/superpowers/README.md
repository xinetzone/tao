# Superpowers: 长期知识沉淀区

本目录存储 AgentForge 项目的长期设计、规划、复盘与记忆资产。

## 四层结构

| 层级 | 目录 | 用途 | 何时创建 | 何时回流 |
|-----|------|------|---------|---------|
| 设计 | `specs/` | 设计蓝图、决策依据 | 需求提案期 | → 落地为规则/工作流 |
| 计划 | `plans/` | 执行计划、任务分解 | 实施前规划 | → 作为复盘的输入 |
| 复盘 | `retrospectives/` | 单次任务的完整记录 | 任务完成后 | → 提取记忆候选 |
| 记忆 | `memories/` | 已沉淀的可复用知识 | 复盘后提取 | → 做梦 → 回流至 rules/ |

## 检索指南

| 需求 | 去向 |
|------|------|
| 理解"为什么这样设计" | `specs/` |
| 追踪"当时的执行计划" | `plans/` |
| 了解"工作的完整总结" | `retrospectives/` |
| 学习"已沉淀的可复用知识" | `memories/` |

## 记忆条目格式

`memories/` 中的条目按 [`../templates/agent-memory-entry-template.md`](../templates/agent-memory-entry-template.md) 格式编写。

完整协议见 [`../references/agent-memory-dream-protocol.md`](../references/agent-memory-dream-protocol.md)。
