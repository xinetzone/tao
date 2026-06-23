# 模块目录清单

> **维护责任人**：Leader Agent
> **更新日期**：2026-06-23
> **适用范围**：`plans/` 全目录

本文件列出 `plans/` 目录下 6 个一级模块的路径、功能、计划数、文件数与维护者，作为模块化重构后的稳定索引。

## 模块总览

| # | 模块 | 路径 | 主题 | 计划数 | 文件数 | 维护者 | 入口 |
|---|------|------|------|--------|--------|--------|------|
| 1 | AI 文档系统 | `ai-docs/` | AI 文档导航、检索关键词、参考维基 | 3 | 8 | Leader Agent | [README](../ai-docs/README.md) |
| 2 | 智能体系统 | `agent-system/` | 协作元模型、记忆协议、角色审查、上下文优化、Token 优化 | 5 | 21 | Leader Agent | [README](../agent-system/README.md) |
| 3 | 探索任务 | `exploration/` | CLI 诊断、引用完整性、模板复用、知识驱动探索 | 4 | 16 | Leader Agent | [README](../exploration/README.md) |
| 4 | GitHub 集成 | `github-integration/` | GitHub App 令牌覆盖、PyGithub 适配 | 2 | 14 | Leader Agent | [README](../github-integration/README.md) |
| 5 | 文档治理 | `docs-governance/` | 业务映射框架、初始化输出、记忆重构计划 | 3 | 8 | Leader Agent | [README](../docs-governance/README.md) |
| 6 | Python 环境 | `python-environment/` | mise 单一事实来源 | 1 | 7 | Leader Agent | [index](../python-environment/2026-05-23-mise-single-source-foundation/index.md) |

**合计**：6 个模块，18 个计划，74 份 .md 文件（不含模块 README 与 _meta）。

## 模块详情

### 1. ai-docs — AI 文档系统

- **路径**：`plans/ai-docs/`
- **功能**：存储与 AI 文档系统构建相关的计划，包括 AI 参考维基搭建、文档导航设计、搜索关键词策略，为 AI 智能体提供结构化参考知识库与检索入口。
- **计划清单**：

| 计划 | 类型 | 文件数 | 说明 |
|------|------|--------|------|
| `2026-05-22-ai-docs-navigation.md` | 单文件 | 1 | AI 文档导航结构设计 |
| `2026-05-22-ai-docs-search-keywords.md` | 单文件 | 1 | AI 文档搜索关键词策略 |
| `2026-05-22-ai-reference-wiki/` | 原子化目录 | 6 | AI 参考维基搭建（含 index + 5 个任务单元） |

### 2. agent-system — 智能体系统

- **路径**：`plans/agent-system/`
- **功能**：存储与智能体系统设计、协作机制、记忆协议相关的计划，涵盖协作元模型、做梦协议、角色评审工作流、上下文结构优化与 Token 减量等主题。
- **计划清单**：

| 计划 | 类型 | 文件数 | 说明 |
|------|------|--------|------|
| `2026-05-24-agent-context-structure-optimization.md` | 单文件 | 1 | 智能体上下文结构优化 |
| `2026-05-24-agent-token-reduction-guide.md` | 单文件 | 1 | 智能体 Token 减量指南 |
| `2026-05-24-agent-collaboration-metamodel/` | 原子化目录 | 5 | 协作元模型（含 index + 4 个任务单元） |
| `2026-05-24-agent-memory-dream-protocol/` | 原子化目录 | 8 | 记忆做梦协议（含 index + overview + file-structure + self-review + 4 个任务单元） |
| `2026-05-24-role-review-workflow/` | 原子化目录 | 6 | 角色评审工作流（含 index + 5 个任务单元） |

### 3. exploration — 探索任务

- **路径**：`plans/exploration/`
- **功能**：存储与探索任务相关的计划，包括 CLI 状态诊断、引用完整性检查、模板复用检查、知识驱动探索基础，为探索性任务提供结构化执行框架与验证记录。
- **计划清单**：

| 计划 | 类型 | 文件数 | 说明 |
|------|------|--------|------|
| `2026-05-24-cli-status-diagnostics-exploration/` | 原子化目录 | 3 | CLI 状态诊断探索（含 index + exploration-check + retrospective） |
| `2026-05-24-exploration-reference-integrity-check/` | 原子化目录 | 3 | 引用完整性检查（含 index + check-record + retrospective） |
| `2026-05-24-exploration-template-reuse-check/` | 原子化目录 | 3 | 模板复用检查（含 index + check-record + retrospective） |
| `2026-05-24-knowledge-driven-exploration-foundation/` | 原子化目录 | 7 | 知识驱动探索基础（含 index + 6 个任务单元） |

### 4. github-integration — GitHub 集成

- **路径**：`plans/github-integration/`
- **功能**：存储与 GitHub 集成相关的计划，包括 GitHub App 安装令牌覆盖机制与 PyGithub 适配器实现，为 GitHub API 调用提供认证、缓存、降级与适配层设计方案。
- **计划清单**：

| 计划 | 类型 | 文件数 | 说明 |
|------|------|--------|------|
| `2026-05-22-github-app-installation-token-override/` | 原子化目录 | 10 | GitHub App 令牌覆盖（含 index + file-structure + 6 个任务单元 + metrics-comparison + plan-self-review） |
| `2026-05-22-pygithub-adapter/` | 原子化目录 | 4 | PyGithub 适配器（含 index + 3 个任务单元） |

### 5. docs-governance — 文档治理

- **路径**：`plans/docs-governance/`
- **功能**：存储与文档治理相关的计划，包括初始化引导产出、记忆模块化重构、道业务映射框架，为文档体系的治理、模块化与业务对齐提供设计依据与执行方案。
- **计划清单**：

| 计划 | 类型 | 文件数 | 说明 |
|------|------|--------|------|
| `2026-05-23-init-onboarding-output.md` | 单文件 | 1 | 初始化引导产出 |
| `2026-06-23-memories-modular-refactor-plan.md` | 单文件 | 1 | 记忆模块化重构计划 |
| `2026-05-23-dao-business-mapping-framework/` | 原子化目录 | 6 | 道业务映射框架（含 index + 5 个任务单元） |

### 6. python-environment — Python 环境

- **路径**：`plans/python-environment/`
- **功能**：存储与 Python 环境管理相关的计划，使 `mise.toml` 成为工具层版本单一事实来源，确保推荐入口稳定可用。
- **计划清单**：

| 计划 | 类型 | 文件数 | 说明 |
|------|------|--------|------|
| `2026-05-23-mise-single-source-foundation/` | 原子化目录 | 7 | mise 单一事实来源（含 index + file-structure + 4 个任务单元 + plan-self-review） |

## 文件类型分布

| 文件类型 | 命名模式 | 数量 | 说明 |
|---------|---------|------|------|
| 单文件计划 | `YYYY-MM-DD-{topic}.md` | 6 | 未拆分的独立计划 |
| 原子化目录 | `YYYY-MM-DD-{topic}/` | 12 | 已拆分的计划目录 |
| 索引文件 | `index.md` | 12 | 原子化目录的入口与单元索引 |
| 任务单元 | `task-N-{name}.md` | 38 | 原子化拆分后的任务单元 |
| 结构说明 | `file-structure.md` | 3 | 文件结构与职责映射 |
| 自审文档 | `plan-self-review.md` | 2 | 计划自查 |
| 复盘记录 | `retrospective.md` | 3 | 探索任务复盘 |
| 检查记录 | `check-record.md` / `exploration-check.md` | 3 | 探索检查记录 |
| 概览文档 | `overview.md` | 1 | 计划概览 |
| 指标对比 | `metrics-comparison.md` | 1 | 改造前后指标对照 |
| 模块 README | `README.md` | 5 | 模块说明与文件清单 |
| 元数据 | `_meta/*.md` | 4 | 命名规范、目录清单、依赖图谱、迁移日志 |
