# Specs: 设计蓝图

> **维护责任人**：Leader Agent
> **模块化日期**：2026-06-23

本目录存储 AgentForge 项目的设计蓝图、决策依据。经模块化重构后，设计文档按主题分为 5 个模块。

## 定位
- **specs/** 关注"为什么这样设计" — 记录设计目标、架构决策、方案选型
- 与 `references/`（参考实现）和 `rules/`（执行规则）形成互补：specs 给出决策依据，references 给出可查阅的标准化产物，rules 给出可执行的约束

## 模块导航
| 模块 | 主题 | 文件数 | 说明 | 入口 |
|------|------|--------|------|------|
| `ai-docs/` | AI 文档系统 | 3 | AI 文档导航、检索关键词、参考 wiki 设计 | [README](./ai-docs/README.md) |
| `agent-system/` | 智能体系统 | 3 | 协作元模型、记忆协议、角色审查设计 | [README](./agent-system/README.md) |
| `github-integration/` | GitHub 集成 | 2 | GitHub App 令牌覆盖、PyGithub 适配设计 | [README](./github-integration/README.md) |
| `task-summaries/` | 任务总结 | 2 | 任务总结描述压缩、最小修复设计 | [README](./task-summaries/README.md) |
| `misc/` | 其他 | 3 | 业务映射框架、mise、知识驱动探索设计 | [README](./misc/README.md) |

> 文件数统计以"原始设计文档"为单位；原子化目录（如 `2026-05-24-agent-collaboration-metamodel-design/`）视为 1 份原始文档。

## 命名规范

完整规范见 [`_meta/naming-convention.md`](./_meta/naming-convention.md)，要点摘要：

| 规则 | 说明 | 示例 |
|------|------|------|
| 单文件命名 | `YYYY-MM-DD-{topic}-design.md` | `2026-05-22-ai-docs-navigation-design.md` |
| 原子化目录 | `YYYY-MM-DD-{topic}-design/` + `index.md` + `part-{序号}-{主题}.md` | `2026-05-24-agent-collaboration-metamodel-design/` |
| 一级模块 | 英文 kebab-case，全小写 | `ai-docs/`、`github-integration/` |
| 元数据目录 | 下划线前缀 | `_meta/` |
| 禁止项 | 中文、emoji、空格、大写字母、下划线（`_meta/` 除外） | — |

## 检索指南
| 需求 | 去向 |
|------|------|
| 查找 AI 文档系统设计（导航/搜索/wiki） | `ai-docs/` |
| 查找智能体协作、记忆、角色评审设计 | `agent-system/` |
| 查找 GitHub App 认证、PyGithub 适配设计 | `github-integration/` |
| 查找任务总结描述压缩、最小修复设计 | `task-summaries/` |
| 查找 DAO 业务映射、Mise 治理、知识驱动探索设计 | `misc/` |
| 查找命名规范、模块清单、依赖关系、迁移记录 | `_meta/` |

## 元数据文档
| 文档 | 用途 |
|------|------|
| [`_meta/naming-convention.md`](./_meta/naming-convention.md) | 命名规范 |
| [`_meta/module-catalog.md`](./_meta/module-catalog.md) | 模块目录清单 |
| [`_meta/dependency-graph.md`](./_meta/dependency-graph.md) | 依赖关系图谱 |
| [`_meta/migration-log.md`](./_meta/migration-log.md) | 迁移日志 |
