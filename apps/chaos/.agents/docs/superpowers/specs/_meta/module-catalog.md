# 模块目录清单

> **维护责任人**：Leader Agent
> **更新日期**：2026-06-23

本文档列出 `specs/` 下全部一级模块的路径、功能、文件数与维护者，作为模块化重构后的权威目录索引。

## 模块总览

| # | 模块 | 路径 | 主题 | 原始文件数 | 维护者 | 模块入口 |
|---|------|------|------|-----------|--------|---------|
| 1 | AI 文档系统 | `ai-docs/` | AI 文档导航、检索关键词、参考 wiki 设计 | 3 | Leader Agent | [README](../ai-docs/README.md) |
| 2 | 智能体系统 | `agent-system/` | 协作元模型、记忆协议、角色审查设计 | 3 | Leader Agent | [README](../agent-system/README.md) |
| 3 | GitHub 集成 | `github-integration/` | GitHub App 令牌覆盖、PyGithub 适配设计 | 2 | Leader Agent | [README](../github-integration/README.md) |
| 4 | 任务总结 | `task-summaries/` | 任务总结描述压缩、最小修复设计 | 2 | Leader Agent | [README](../task-summaries/README.md) |
| 5 | 杂项 | `misc/` | 业务映射框架、mise、知识驱动探索设计 | 3 | Leader Agent | [README](../misc/README.md) |

**合计**：5 个模块，13 份原始设计文档。

## 模块详情

### 1. AI 文档系统（`ai-docs/`）

| 文件 | 说明 |
|------|------|
| `2026-05-22-ai-docs-navigation-design.md` | AI 文档导航结构设计 |
| `2026-05-22-ai-docs-search-keywords-design.md` | AI 文档搜索关键词设计 |
| `2026-05-22-ai-reference-wiki-design.md` | AI 参考维基设计 |

- **功能**：指导 AI 文档导航结构、搜索关键词策略与参考维基构建
- **依赖**：无外部依赖

### 2. 智能体系统（`agent-system/`）

| 文件/目录 | 说明 |
|----------|------|
| `2026-05-24-agent-memory-dream-protocol-design.md` | 智能体记忆梦境协议设计 |
| `2026-05-24-role-review-workflow-design.md` | 角色评审工作流设计 |
| `2026-05-24-agent-collaboration-metamodel-design/` | 智能体协作元模型设计（原子化目录，含 index.md + 5 个 part 文件） |

- **功能**：指导智能体协作、记忆治理与角色边界设计
- **依赖**：引用 `apps/chaos/.agents/docs/references/agent-collaboration-metamodel.md`

### 3. GitHub 集成（`github-integration/`）

| 文件 | 说明 |
|------|------|
| `2026-05-22-github-app-installation-token-override-design.md` | GitHub App 安装令牌覆盖设计 |
| `2026-05-22-pygithub-adapter-design.md` | PyGithub 适配器设计 |

- **功能**：指导 GitHub 平台认证授权与 API 适配开发
- **依赖**：无外部依赖（实现层引用 `src/taolib/github_app/` 源码）

### 4. 任务总结（`task-summaries/`）

| 文件 | 说明 |
|------|------|
| `2026-05-20-task-execution-summary-description-compression-design.md` | 任务执行总结描述压缩设计 |
| `2026-05-20-task-execution-summary-minimal-fix-design.md` | 任务执行总结最小化修复设计 |

- **功能**：指导任务总结输出格式优化与最小变更治理
- **依赖**：无外部依赖

### 5. 杂项（`misc/`）

| 文件/目录 | 说明 |
|----------|------|
| `2026-05-23-dao-business-mapping-framework-design.md` | DAO 业务映射框架设计 |
| `2026-05-23-mise-single-source-foundation-design.md` | Mise 单一来源基石设计 |
| `2026-05-24-knowledge-driven-exploration-foundation-design/` | 知识驱动探索基石设计（原子化目录，含 index.md + 13 个 part 文件） |

- **功能**：承载跨领域或暂未独立成模块的设计方案
- **依赖**：无外部依赖

## 维护约定

- 新增模块需经 Leader Agent 审查，并同步更新本清单与 [`README.md`](../README.md) 的模块导航表
- 模块路径、文件数等信息变更后，须同步更新 [`migration-log.md`](./migration-log.md)
- 模块命名遵循 [`naming-convention.md`](./naming-convention.md)
