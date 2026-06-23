# 模块目录清单

> **生成日期**：2026-06-23
> **维护责任人**：Leader Agent
> **原始文件总数**：72
> **模块总数**：6 一级 + 9 二级 = 15 个模块

## 一级模块

| # | 模块路径 | 功能 | 文件数 | 原子化目录数 | 维护者 |
|---|---------|------|--------|-------------|--------|
| 1 | `project-reviews/` | 项目级阶段性全面复盘 | 4 | 1 | Leader Agent |
| 2 | `audit-reports/` | 质量审计与债务评估报告 | 2 | 1 | Leader Agent |
| 3 | `insights/` | 技术洞察与设计反思 | 3 | 0 | Leader Agent |
| 4 | `session-reviews/` | 单次会话复盘 | 1 | 0 | Leader Agent |
| 5 | `task-summaries/` | 任务执行总结（含 9 个二级子模块） | 60 | 3 | Leader Agent |
| 6 | `misc/` | 其他复盘 | 2 | 0 | Leader Agent |

## 二级子模块（task-summaries/ 下）

| # | 子模块路径 | 主题 | 文件数 | 原子化目录数 | 维护者 |
|---|-----------|------|--------|-------------|--------|
| 1 | `task-summaries/ci-cd/` | CI 流水线、lint、构建修复 | 5 | 0 | Leader Agent |
| 2 | `task-summaries/documentation/` | 文档治理、边界重构、changelog | 16 | 0 | Leader Agent |
| 3 | `task-summaries/python-environment/` | Python 版本适配、依赖管理 | 7 | 1 | Leader Agent |
| 4 | `task-summaries/skills/` | 技能资产开发与校验 | 2 | 0 | Leader Agent |
| 5 | `task-summaries/releases/` | 版本发布与后续改进 | 5 | 0 | Leader Agent |
| 6 | `task-summaries/exploration/` | 探索任务与知识循环 | 8 | 0 | Leader Agent |
| 7 | `task-summaries/world-cli/` | World CLI 分发与层级规范 | 3 | 0 | Leader Agent |
| 8 | `task-summaries/refactoring/` | 代码重构任务 | 3 | 1 | Leader Agent |
| 9 | `task-summaries/misc/` | 其他任务总结 | 11 | 1 | Leader Agent |

## 原子化目录

| # | 原子化目录 | 所属模块 | 原始行数 | 原子单元数 | 维护者 |
|---|-----------|---------|---------|-----------|--------|
| 1 | `project-reviews/agentforge-project-retrospective-20260523/` | project-reviews | 575 | 6 | Leader Agent |
| 2 | `audit-reports/audit-report-superpowers-memory-debt-20260611/` | audit-reports | 398 | 4 | Leader Agent |
| 3 | `task-summaries/python-environment/task-summary-lint-python313-20260609/` | python-environment | 878 | 13 | Leader Agent |
| 4 | `task-summaries/misc/task-summary-agentforge-collaboration-system-20260524/` | misc | 777 | 12 | Leader Agent |
| 5 | `task-summaries/refactoring/task-summary-containerrun-refactor-20260610/` | refactoring | 546 | 12 | Leader Agent |

## 元数据模块

| # | 文档路径 | 用途 | 维护者 |
|---|---------|------|--------|
| 1 | `_meta/naming-convention.md` | 命名规范 | Leader Agent |
| 2 | `_meta/module-catalog.md` | 模块目录清单（本文件） | Leader Agent |
| 3 | `_meta/module-mindmap.md` | 模块化结构思维导图（可视化） | Leader Agent |
| 4 | `_meta/dependency-graph.md` | 依赖关系图谱 | Leader Agent |
| 5 | `_meta/migration-log.md` | 迁移日志 | Leader Agent |

## 统计摘要

| 指标 | 数值 |
|------|------|
| 原始文件总数 | 72 |
| 一级模块数 | 6 |
| 二级子模块数 | 9 |
| 原子化目录数 | 5 |
| 原子单元文件总数 | 47 |
| 模块 README 总数 | 15 |
| 元数据文档总数 | 5 |
| 迁移完成率 | 100% (72/72) |
