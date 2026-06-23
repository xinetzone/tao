# Plans: 执行计划

> **维护责任人**：Leader Agent
> **模块化日期**：2026-06-23

本目录存储 AgentForge 项目的执行计划、任务分解。经模块化重构后，计划按主题分为 6 个模块。

## 定位

- **plans/** 关注"怎样执行" — 记录任务分解、执行步骤、交付物清单
- 与 `../../references/` 的"是什么"（参考框架）和 `../../retrospectives/` 的"做得怎样"（复盘记录）形成互补
- 计划文件遵循"先设计后执行"原则，每个计划含目标、架构、任务清单与验收标准

## 模块导航

| 模块 | 主题 | 计划数 | 说明 | 入口 |
|------|------|--------|------|------|
| `ai-docs/` | AI 文档系统 | 3 | AI 文档导航、检索关键词、参考 wiki | [README](./ai-docs/README.md) |
| `agent-system/` | 智能体系统 | 5 | 协作元模型、记忆协议、角色审查、上下文优化、Token 优化 | [README](./agent-system/README.md) |
| `exploration/` | 探索任务 | 4 | CLI 诊断、引用完整性、模板复用、知识驱动探索 | [README](./exploration/README.md) |
| `github-integration/` | GitHub 集成 | 2 | GitHub App 令牌覆盖、PyGithub 适配 | [README](./github-integration/README.md) |
| `docs-governance/` | 文档治理 | 3 | 业务映射框架、初始化输出、记忆重构计划 | [README](./docs-governance/README.md) |
| `python-environment/` | Python 环境 | 1 | mise 单一事实来源 | [README](./python-environment/2026-05-23-mise-single-source-foundation/index.md) |

## 命名规范

本目录遵循 [`_meta/naming-convention.md`](./_meta/naming-convention.md) 的完整规范，要点摘要如下：

| 规则 | 说明 | 示例 |
|------|------|------|
| 目录命名 | 纯 ASCII kebab-case | `ai-docs/`、`agent-system/` |
| 单文件计划 | `YYYY-MM-DD-{topic}.md` | `2026-05-22-ai-docs-navigation.md` |
| 原子化目录 | `YYYY-MM-DD-{topic}/` | `2026-05-22-ai-reference-wiki/` |
| 原子单元 | `{section-name}.md` | `task-1-top-level-directories.md` |
| 索引文件 | `index.md`（原子化目录内）/ `README.md`（模块目录内） | — |
| 元数据目录 | 下划线前缀 | `_meta/` |

## 检索指南

| 需求 | 去向 |
|------|------|
| 查找 AI 文档系统计划（导航、关键词、参考维基） | `ai-docs/` |
| 查找智能体系统计划（协作、记忆、角色、上下文、Token） | `agent-system/` |
| 查找探索任务计划（CLI 诊断、引用检查、模板复用、知识探索） | `exploration/` |
| 查找 GitHub 集成计划（令牌覆盖、PyGithub 适配） | `github-integration/` |
| 查找文档治理计划（业务映射、初始化、记忆重构） | `docs-governance/` |
| 查找 Python 环境计划（mise 单一事实来源） | `python-environment/` |
| 查找命名规范、模块目录、依赖关系、迁移日志 | `_meta/` |
| 查找参考框架（"是什么"） | `../../references/` |
| 查找复盘记录（"做得怎样"） | `../../retrospectives/` |

## 目录结构

```
plans/
├── README.md                    # 本文件：总入口 + 导航索引
├── _meta/                       # 元数据与治理
│   ├── naming-convention.md     # 命名规范
│   ├── module-catalog.md        # 模块目录清单
│   ├── dependency-graph.md      # 依赖关系图谱
│   └── migration-log.md         # 迁移日志
├── ai-docs/                     # AI 文档系统计划
├── agent-system/                # 智能体系统计划
├── exploration/                 # 探索任务计划
├── github-integration/          # GitHub 集成计划
├── docs-governance/             # 文档治理计划
└── python-environment/          # Python 环境计划
```

## 元数据文档

| 文档 | 用途 |
|------|------|
| [`_meta/naming-convention.md`](./_meta/naming-convention.md) | 命名规范（目录、文件、日期格式、审计自检） |
| [`_meta/module-catalog.md`](./_meta/module-catalog.md) | 模块目录清单（6 个模块的路径、功能、文件数、维护者） |
| [`_meta/dependency-graph.md`](./_meta/dependency-graph.md) | 依赖关系图谱（文档间引用、模块间依赖、Mermaid 可视化） |
| [`_meta/migration-log.md`](./_meta/migration-log.md) | 迁移日志（覆盖全部 27 份原始文件的迁移与校验记录） |
