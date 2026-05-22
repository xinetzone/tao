# AI Reference Wiki Design

## Goal

为 `AgentForge` 建立一套面向 AI 智能体的参考 wiki 组织方案，用于沉淀 Python 包知识、Podman 使用与排障知识，以及这些外部知识与仓库内部实现之间的映射关系，帮助 agent 在排查问题时更快定位正确文档、命令和代码入口。

本次设计目标如下：

- 保持人类文档与 AI 文档严格隔离
- 让“概念参考”“故障排查”“项目映射”“原始来源”四类知识各归其位
- 控制高频检索路径的层级与命名复杂度
- 为后续批量抓取、精炼与持续更新预留稳定骨架

## Background

当前仓库已经明确区分：

- `docs/` 目录面向人类开发者
- `.agents/docs/` 目录面向 AI 智能体
- `.agents/docs/superpowers/` 用于设计文档、计划与复盘沉淀

这一边界已经足够清晰，但 `.agents/docs/` 目前仍以项目级说明、迁移记录和版本跟踪为主，尚未形成一套适合 agent 高频检索的“外部知识参考区”。

如果直接把 Python 包、Podman 官方资料和实践笔记堆放到单一 `wiki/` 目录中，短期可用，但后续会出现以下问题：

- 文档类型混杂，agent 难以快速判断应该优先读取哪一类文件
- 外部原始资料与项目内消化后的知识没有分层，检索噪声会增加
- 同一问题的“概念解释”“常见报错”和“项目中该看哪里”会散落在多个大文件中

因此，需要在 `.agents/docs/` 下新增一套低耦合、可持续扩展的知识结构。

## Scope

- 在 `.agents/docs/` 下新增 AI 参考 wiki 的目录骨架
- 明确一级知识区的职责边界
- 为 `python/` 与 `podman/` 两个主题建立起始目录
- 为每个目录提供最小 `README.md` 导航
- 提供可复用的单页模板，统一文档结构
- 创建少量种子页占位，方便后续逐步填充

## Non-Goals

- 本次不批量抓取和导入大量外部文档
- 本次不将原始来源自动转换成结构化知识图谱
- 本次不改动面向人类的 `docs/` 文档树
- 本次不把设计文档、复盘文档混入参考 wiki 目录
- 本次不实现搜索脚本、索引生成器或自动同步流程

## Design Principles

1. 文档边界清晰：AI 参考 wiki 只放在 `.agents/docs/`，不侵入 `docs/`。
2. 职责单一：每个一级目录只承载一种知识类型，避免混放。
3. 检索优先：优先优化 agent 的“先看什么”决策，而不是为人类浏览构建复杂层级。
4. 来源可追溯：原始抓取内容和精炼知识分开存放，确保可回溯。
5. 渐进扩展：先搭骨架和模板，再逐步补充高价值主题。

## Current Assessment

当前 `.agents/docs/` 已具备如下基础：

- 有清晰的 AI 文档边界说明
- 已存在长期沉淀目录 `.agents/docs/superpowers/`
- 命名风格以小写加连字符为主
- 高价值知识文档通常为单主题 Markdown 文件

这意味着新 wiki 不需要重新发明一套规范，而是应延续已有约定，在 `.agents/docs/` 下新增一个面向“参考知识”的稳定子结构。

## Options Considered

### Option A: 单层 `wiki/` 目录

建议结构：

- `.agents/docs/wiki/`

优点：

- 创建成本最低
- 初期目录最简单

缺点：

- 文档类型会快速混杂
- 不利于 agent 区分参考、排障、集成和来源
- 后期重构成本高

### Option B: 四层知识库

建议结构：

- `.agents/docs/references/`
- `.agents/docs/issue-patterns/`
- `.agents/docs/integrations/`
- `.agents/docs/sources/`

优点：

- 目录语义清晰
- 最适合 agent 快速判断读取顺序
- 支持持续扩展且不易失控

缺点：

- 初始目录略多
- 需要统一模板和命名规范

### Option C: 按技术域顶层拆分

建议结构：

- `.agents/docs/python/`
- `.agents/docs/podman/`

优点：

- 从主题角度看比较直观

缺点：

- “问题模式”和“项目映射”会在多个技术域下重复出现
- 跨领域问题难以统一组织

## Recommendation

采用 Option B，并在 `references/` 与 `sources/` 下按技术域进一步拆分。

推荐结构如下：

```text
.agents/docs/
  references/
    README.md
    python/
      README.md
      package-index.md
    podman/
      README.md
      command-cheatsheet.md
  issue-patterns/
    README.md
    python-errors.md
    podman-errors.md
  integrations/
    README.md
    python-in-agentforge.md
    podman-in-agentforge.md
  sources/
    README.md
    python/
      README.md
    podman/
      README.md
  templates/
    reference-page-template.md
```

## Directory Responsibilities

### `references/`

用于存放经过提炼、适合 agent 直接阅读的主题知识页。

适合内容：

- Python 包能力总结
- Podman 场景化操作说明
- 常用概念、约束、命令速查

不适合内容：

- 冗长原始抓取结果
- 项目实施 spec
- 任务复盘

### `issue-patterns/`

用于存放按“现象 -> 原因 -> 排查 -> 对应文件/命令”组织的故障模式文档。

适合内容：

- Python 依赖、版本、测试、类型相关错误模式
- Podman 镜像、挂载、网络、权限相关错误模式

### `integrations/`

用于存放外部知识与本仓库实现之间的映射。

适合回答这类问题：

- 这个 Python 包在本项目哪里出现
- Podman 在本项目的哪个工作流或脚本里相关
- 某类问题优先检查哪些代码和配置文件

### `sources/`

用于存放原始抓取材料、官方文档节选或尚未精炼的工作底稿。

要求：

- 不作为 agent 默认优先阅读入口
- 每份材料尽量保留来源链接、抓取时间和版本信息

### `templates/`

用于存放可复制的文档模板，保证新页面结构稳定一致。

## Document Shape

所有参考页建议采用统一结构：

```md
# Topic Title

## Goal

一句话说明该页回答什么问题。

## Relevance In AgentForge

- 关联模块：
- 常见触发场景：
- 优先检查文件：

## Key Concepts

- 概念 A：
- 概念 B：

## Common Problems

### 问题：示例

- 现象：
- 原因：
- 排查步骤：
- 相关命令或代码位置：

## Commands Or Snippets

```bash
# example
```

## Sources

- 官方文档：
- 版本：
- 抓取时间：
```

## Naming Conventions

- 目录名统一使用小写
- 文件名统一使用小写加连字符
- 包级页面优先使用真实包名，如 `pytest.md`、`httpx.md`
- 场景页使用问题域命名，如 `volumes-and-mounts.md`、`networking.md`
- 避免使用 `notes-final`、`misc`、`temp` 等弱语义命名

## Seed Files

建议首批创建以下文件：

- `.agents/docs/references/README.md`
- `.agents/docs/references/python/README.md`
- `.agents/docs/references/python/package-index.md`
- `.agents/docs/references/podman/README.md`
- `.agents/docs/references/podman/command-cheatsheet.md`
- `.agents/docs/issue-patterns/README.md`
- `.agents/docs/issue-patterns/python-errors.md`
- `.agents/docs/issue-patterns/podman-errors.md`
- `.agents/docs/integrations/README.md`
- `.agents/docs/integrations/python-in-agentforge.md`
- `.agents/docs/integrations/podman-in-agentforge.md`
- `.agents/docs/sources/README.md`
- `.agents/docs/sources/python/README.md`
- `.agents/docs/sources/podman/README.md`
- `.agents/docs/templates/reference-page-template.md`

## Rollout Plan

建议按以下顺序落地：

1. 创建四个一级知识区目录与 `templates/`
2. 为每个目录添加说明性 `README.md`
3. 创建 `python/` 与 `podman/` 起始目录
4. 创建种子页占位文件
5. 后续按价值优先级逐步填充内容，而不是一次性导入全部资料

## Risks

- 如果把原始资料直接堆入 `references/`，会削弱目录分层的价值
- 如果缺少统一模板，不同页面质量会很快分化
- 如果后续不维护 `integrations/`，外部知识与仓库实现之间的连接会变弱

## Acceptance Criteria

- 新增结构完全位于 `.agents/docs/` 下
- 不修改 `docs/` 面向人类的文档树
- 新增目录职责可通过 `README.md` 一眼看懂
- 至少具备 `python` 与 `podman` 两个技术域入口
- 至少具备 1 个可复制的通用模板
- 新结构不会与 `.agents/docs/superpowers/` 的设计/复盘归档职责冲突
