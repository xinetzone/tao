# Retrospectives — 复盘知识资产区

> **维护责任人**：Leader Agent
> **重构日期**：2026-06-23
> **原始文件数**：72 → **模块化重构后**：6 个一级模块 + 9 个二级子模块 + 5 个原子化目录

本目录存储 AgentForge 项目的复盘、审计、洞察与会话记录等长期沉淀资产。经 2026-06-23 模块化重构，已从扁平结构升级为**原子化、模块化、结构化**的组织形式。

## 模块导航

| 模块 | 用途 | 文件数 | 入口 |
|------|------|--------|------|
| `project-reviews/` | 项目级阶段性全面复盘 | 4 | [README](./project-reviews/README.md) |
| `audit-reports/` | 质量审计与债务评估报告 | 2 | [README](./audit-reports/README.md) |
| `insights/` | 技术洞察与设计反思 | 3 | [README](./insights/README.md) |
| `session-reviews/` | 单次会话复盘 | 1 | [README](./session-reviews/README.md) |
| `task-summaries/` | 任务执行总结（含 9 个主题子模块） | 60 | [README](./task-summaries/README.md) |
| `misc/` | 其他复盘（微信归档、知乎推广等） | 2 | [README](./misc/README.md) |

### task-summaries 二级子模块

| 子模块 | 主题 | 文件数 | 入口 |
|--------|------|--------|------|
| `ci-cd/` | CI 流水线、lint、构建修复 | 5 | [README](./task-summaries/ci-cd/README.md) |
| `documentation/` | 文档治理、边界重构、changelog | 16 | [README](./task-summaries/documentation/README.md) |
| `python-environment/` | Python 版本适配、依赖管理 | 7 | [README](./task-summaries/python-environment/README.md) |
| `skills/` | 技能资产开发与校验 | 2 | [README](./task-summaries/skills/README.md) |
| `releases/` | 版本发布与后续改进 | 5 | [README](./task-summaries/releases/README.md) |
| `exploration/` | 探索任务与知识循环 | 8 | [README](./task-summaries/exploration/README.md) |
| `world-cli/` | World CLI 分发与层级规范 | 3 | [README](./task-summaries/world-cli/README.md) |
| `refactoring/` | 代码重构任务 | 3 | [README](./task-summaries/refactoring/README.md) |
| `misc/` | 其他任务总结 | 11 | [README](./task-summaries/misc/README.md) |

## 原子化拆分目录

以下 5 份大型文档已按主题拆分为原子单元目录，每个目录含 `index.md` 索引与多个专注单一主题的原子单元文件：

| 原子化目录 | 原始行数 | 原子单元数 | 位置 |
|-----------|---------|-----------|------|
| `agentforge-project-retrospective-20260523/` | 575 | 6 | [index](./project-reviews/agentforge-project-retrospective-20260523/index.md) |
| `audit-report-superpowers-memory-debt-20260611/` | 398 | 4 | [index](./audit-reports/audit-report-superpowers-memory-debt-20260611/index.md) |
| `task-summary-lint-python313-20260609/` | 878 | 13 | [index](./task-summaries/python-environment/task-summary-lint-python313-20260609/index.md) |
| `task-summary-agentforge-collaboration-system-20260524/` | 777 | 12 | [index](./task-summaries/misc/task-summary-agentforge-collaboration-system-20260524/index.md) |
| `task-summary-containerrun-refactor-20260610/` | 546 | 12 | [index](./task-summaries/refactoring/task-summary-containerrun-refactor-20260610/index.md) |

## 元数据与治理

| 文档 | 用途 |
|------|------|
| [`_meta/naming-convention.md`](./_meta/naming-convention.md) | 命名规范（目录名、文件名、日期格式） |
| [`_meta/module-catalog.md`](./_meta/module-catalog.md) | 模块目录清单（路径、功能、文件数、维护者） |
| [`_meta/dependency-graph.md`](./_meta/dependency-graph.md) | 依赖关系图谱（正向/反向依赖、模块间关系） |
| [`_meta/migration-log.md`](./_meta/migration-log.md) | 迁移日志（72 份原始文件迁移记录） |

## 命名规范摘要

- **目录名**：纯 ASCII 英文 kebab-case
- **文件名**：`{topic}-{date}.md` 或 `{section-name}.md`（原子单元）
- **日期格式**：YYYYMMDD
- **禁止**：中文、emoji、空格

完整规范见 [`_meta/naming-convention.md`](./_meta/naming-convention.md)。

## 检索指南

| 需求 | 去向 |
|------|------|
| 了解项目整体进展与目标达成 | `project-reviews/` |
| 查看质量审计与债务评估 | `audit-reports/` |
| 学习技术设计反思与洞察 | `insights/` |
| 回顾单次会话完整过程 | `session-reviews/` |
| 查找特定任务的执行总结 | `task-summaries/{theme}/` |
| 查看大型文档的特定主题 | 对应原子化目录的 `index.md` |
| 了解模块间引用关系 | `_meta/dependency-graph.md` |
| 查看迁移完整性 | `_meta/migration-log.md` |

## 与上层结构的关系

本目录属于 `superpowers/` 四层结构之一：

| 层级 | 目录 | 用途 |
|------|------|------|
| 设计 | `../specs/` | 设计蓝图、决策依据 |
| 计划 | `../plans/` | 执行计划、任务分解 |
| **复盘** | **`./`（本目录）** | **任务完成后的完整记录** |
| 记忆 | `../memories/` | 已沉淀的可复用知识 |

复盘完成后，可复用知识提取至 `../memories/`，经做梦协议回流至 `../../rules/`。
