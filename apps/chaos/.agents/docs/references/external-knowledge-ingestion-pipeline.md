# 外部知识入库流水线

> 来源洞察：从 Hello-Agents 教程知识萃取任务中提炼出的 AgentForge 流程资产。
>
> 相关参考：[`projects/hello-agents/index.md`](./projects/hello-agents/index.md)、[`agent-runtime-closed-loop.md`](./agent-runtime-closed-loop.md)、[`web-content-extraction-patterns.md`](./web-content-extraction-patterns.md)、[`doc-maintenance-workflow.md`](./doc-maintenance-workflow.md)

## 定位

外部知识入库流水线用于将外部 URL、教程站、官方文档、课程资料或开源项目 README 转化为 AgentForge 内部可检索、可追溯、可验证、可提交的知识资产。

它的目标不是生成一次性网页摘要，而是生产项目内长期可复用的知识结构：原始资料进入 `sources/`，稳定萃取进入 `references/`，索引入口负责后续发现，校验命令负责质量闭环，复盘和记忆负责长期经验沉淀。

这个流程可以作为未来 AgentForge 的标准工作流、脚本或 skill 的设计基础，候选命名包括：

```text
external-knowledge-ingestion
tutorial-extraction-pipeline
source-to-reference-ingestion
```

## 核心洞察

外部知识入库不是“把网页内容搬进项目”，而是把外部资料转化为项目语义资产。

高质量入库至少回答四个问题：

| 问题 | 对应资产 | 说明 |
|---|---|---|
| 原文是什么？ | `sources/` | 保留原始资料、章节、来源链接、抓取范围和 manifest |
| 我们怎么理解？ | `references/` | 按 AgentForge 语义重组核心概念、步骤、案例和项目映射 |
| 后续怎么找到？ | README 索引、Search Keywords、Trigger Phrases | 让人类和 Agent 都能稳定召回这份知识 |
| 质量如何证明？ | 链接检查、结构检查、复盘、原子提交 | 让知识资产可验证、可追溯、可维护 |

“全部内容”不等于全文复制。完整性应由目录覆盖、来源追溯、核心概念、操作步骤、关键案例、项目映射和校验闭环共同证明。

## 标准流水线

外部知识入库可以抽象为以下流程：

```{mermaid}
flowchart TD
    A["外部 URL"] --> B["识别真实源"]
    B --> C["抓取目录"]
    C --> D["抓取章节"]
    D --> E["生成 manifest"]
    E --> F["原始资料入 sources"]
    F --> G["结构化萃取入 references"]
    G --> H["更新索引"]
    H --> I["链接检查"]
    I --> J["生成复盘"]
    J --> K["原子提交"]
```

### 1. 外部 URL

输入可以是教程首页、文档站入口、GitHub Pages、官方文档、课程目录、README 或文章集合。入口 URL 只是线索，不应默认等于真实源。

需要记录：

- 用户提供的入口。
- 任务目标和范围。
- 是否要求全量章节、重点章节还是主题摘要。
- 是否需要映射到 AgentForge 的已有目录、规则或架构概念。

### 2. 识别真实源

文档站、教程站和 GitHub Pages 经常只是展示层。真实源可能位于 GitHub 仓库、Markdown 文件、docs 目录、静态站点源文件或发布分支。

优先识别真实源可以降低遗漏风险：

| 表层入口 | 可能真实源 | 处理建议 |
|---|---|---|
| Docsify / GitHub Pages 首页 | GitHub Markdown 仓库 | 优先抓取仓库目录和 Markdown 文件 |
| 官方文档首页 | 文档侧边栏、站点地图、版本目录 | 先确认版本与章节范围 |
| 单篇文章 | 原始 Markdown、RSS、作者仓库 | 保存文章元信息和发布日期 |
| 课程站 | 章节列表、教材仓库、Notebook | 保留章节顺序和实践材料 |

### 3. 抓取目录

目录抓取负责确定知识边界。目录不完整，后续萃取就很容易漏章。

目录阶段至少应形成：

- 章节列表。
- 标题层级。
- 原始链接。
- 本地目标文件名。
- 抓取状态。

### 4. 抓取章节

章节抓取应尽量保留原始语义结构，避免在 raw source 阶段过度改写。必要清洗可以做，但应以不破坏追溯为原则。

需要特别注意：

- 外部文档中的占位链接。
- 本地路径、示例用户名、临时下载地址。
- Markdown 中看似链接但实际是语法示例的内容。
- 站点相对链接在本项目中的有效性。

### 5. 生成 manifest

manifest 是 sources 层的目录账本，用于回答“抓了什么、从哪里来、存到哪里”。

典型字段可以包括：

| 字段 | 作用 |
|---|---|
| `title` | 章节标题 |
| `source_url` | 原始链接 |
| `local_path` | 本地归档路径 |
| `order` | 章节顺序 |
| `status` | 抓取状态 |
| `notes` | 特殊说明，例如占位链接已清洗 |

manifest 不一定必须统一为某种格式，但应足以支持后续检查覆盖率和追溯来源。

### 6. 原始资料入 sources

`sources/` 存放原始资料、抓取结果和工作底稿，回答“原文是什么”。

典型目录结构：

```text
.agents/docs/sources/<topic>/
├── chapters-manifest.json
├── github-readme.md
├── 00-preface.md
├── 01-<chapter>.md
└── ...
```

sources 层应尽量保留外部资料的结构和来源，但也要避免明显无效链接污染项目链接检查。

### 7. 结构化萃取入 references

`references/` 存放提炼后的稳定知识页，回答“这对 AgentForge 意味着什么”。

萃取页不应只是原文摘要，而应包含：

- 定位。
- 学习路径或逻辑结构。
- 核心概念。
- 操作步骤。
- 实践案例。
- 与 AgentForge 的映射。
- 可迁移原则。
- Search Keywords。
- Trigger Phrases。

若主题来自某个外部项目或教程，适合放在 `references/projects/<topic>/index.md`。若主题已经抽象为通用流程、原则或架构参考，适合放在 `references/<topic>.md`。

### 8. 更新索引

索引让知识资产可发现。没有索引的稳定页容易成为孤立文件。

通常需要更新：

- `references/README.md`。
- `references/projects/index.md`，如果落在 projects 子目录。
- `sources/README.md`，如果新增了 raw source 目录。
- 其他与项目导航相关的 README。

### 9. 链接检查

外部 Markdown 很容易携带无效链接。入库后应至少做目标链接检查。

常见问题包括：

| 问题 | 示例 | 处理方式 |
|---|---|---|
| 占位链接 | `百度网盘（链接）` | 转为纯文本或补充真实链接 |
| 示例用户名链接 | `https://github.com/你的用户名/...` | 转为纯文本示例 |
| 函数调用被识别为链接 | `tool_name(**kwargs)` | 改写为代码文本或转义 |
| 站点相对链接失效 | `../chapter-1` | 改为本地相对路径或纯文本说明 |

链接检查失败时，应区分新引入问题和仓库既有问题。只修复与本次入库直接相关的问题，避免扩大变更范围。

### 10. 生成复盘

当外部知识入库任务较大、出现失败修复、形成新流程或用户要求复盘时，应生成 retrospectives 报告。

复盘重点不是重复萃取内容，而是记录：

- 任务目标。
- 实际产物。
- 验证命令。
- 遇到的问题。
- 修复策略。
- 可复用流程。
- 后续可回流的记忆或规则。

### 11. 原子提交

外部知识入库通常会同时修改 spec、sources、references、索引、复盘和记忆。是否属于一个原子提交，应按“知识资产闭环”判断，而不是按文件数量判断。

一个合理的原子提交可以包含：

```text
为什么做 → 原文是什么 → 我们怎么理解 → 后续怎么找到 → 如何验证
```

但不应混入无关任务、其他主题的临时文件或既有未完成改动。

## 输入与输出

### 输入

| 输入 | 说明 |
|---|---|
| 外部入口 | URL、仓库、文档站、课程页、README、文章集合 |
| 主题名称 | 用于生成目录名、文件名和索引标题 |
| 范围要求 | 全量、重点章节、指定主题、指定文件 |
| 目标读者 | Agent、开发者、架构设计者、学习者 |
| 项目映射需求 | 是否需要映射到 AgentForge 的 rules、references、runtime、workflow 或目录结构 |
| 验收标准 | 完整性、准确性、可追溯性、可检索性、校验通过 |

### 输出

| 输出 | 说明 |
|---|---|
| `sources/<topic>/` | 原始资料、章节归档、manifest |
| `references/<topic>.md` 或 `references/projects/<topic>/index.md` | 稳定萃取页 |
| 索引入口 | README 或项目导航中的链接 |
| 校验记录 | 链接检查、格式检查、结构检查结果 |
| 复盘报告 | 可选，适用于复杂或高价值任务 |
| 记忆条目 | 可选，适用于长期原则、经验或约束 |
| 原子提交 | 可选，用户明确要求提交时执行 |

## 目录放置规则

| 内容类型 | 推荐位置 | 判断标准 |
|---|---|---|
| 原始网页、章节、README、抓取结果 | `sources/` | 需要保留原文、追溯来源或抓取范围 |
| 提炼后的稳定知识页 | `references/` | 可长期复用，可被 Agent 检索和引用 |
| 外部项目教程萃取 | `references/projects/<topic>/` | 主题主要绑定某个外部项目或教程 |
| 通用流程或架构原则 | `references/<topic>.md` | 已经从单个项目抽象为通用参考 |
| 问题模式和排障路径 | `issue-patterns/` | 围绕错误现象、触发条件和修复路径组织 |
| 历史计划、设计、复盘 | `superpowers/` | 记录任务过程、决策背景或长期经验沉淀 |
| 长期记忆候选 | `superpowers/memories/` | 按记忆模板沉淀原则、经验、约束或反例 |

## 质量标准

外部知识入库的质量应从七个维度判断：

| 维度 | 标准 | 常见检查方式 |
|---|---|---|
| 覆盖完整性 | 章节、目录、核心主题没有明显遗漏 | manifest、目录对照、章节索引 |
| 来源追溯 | 能找到入口、真实源和本地归档路径 | source_url、local_path、README |
| 结构清晰 | 萃取页按学习路径、概念、步骤、案例组织 | references 页面结构 |
| 项目映射 | 明确外部知识对 AgentForge 的意义 | 映射表、可迁移原则 |
| 链接卫生 | 无效占位链接和错误相对路径不污染项目 | linkcheck、diff check |
| 可检索性 | 包含 Search Keywords 和 Trigger Phrases | 页面固定章节 |
| 提交边界 | 只包含同一知识资产闭环内的变更 | git status、git diff、显式 staging |

## 可产品化方向

这条流水线可以逐步产品化为 AgentForge 的标准能力。

### Workflow 形态

作为工作流时，它可以是一组人工与 Agent 协同步骤：

```text
确认范围 → 识别真实源 → 归档 sources → 萃取 references → 更新索引 → 校验 → 复盘 → 提交
```

适合当前阶段，因为它不要求复杂自动化，且能保留人工判断。

### Script 形态

作为脚本时，可以先自动化稳定且低风险的部分：

- 生成目录骨架。
- 生成 manifest 模板。
- 检查 sources 与 references 是否有索引入口。
- 执行目标链接检查。
- 检查 Search Keywords 和 Trigger Phrases 是否存在。

脚本不应过早承担“理解原文并萃取核心知识”的职责，除非已有可靠评估机制。

### Skill 形态

作为 skill 时，可以封装完整知识入库协议：

- 输入 URL 和目标范围。
- 判断真实源。
- 规划 sources / references 输出结构。
- 指导抓取与萃取。
- 生成质量检查清单。
- 输出原子提交建议。

skill 的价值不只是自动化步骤，而是固化判断标准：何时放 sources，何时放 references，何时生成 memories，何时只做临时摘要。

## 风险与边界

### 避免把临时摘要误归档为长期知识

不是所有网页都值得进入 references。一次性摘要、临时调研、低可信内容或没有后续复用价值的资料，可以停留在临时文件或任务回答中。

### 避免只抓入口页

很多文档站首页只包含导航或介绍。若用户要求“全部内容”，必须追溯章节目录和真实源，否则会形成不完整知识资产。

### 避免污染链接检查

外部 Markdown 常包含占位链接、示例链接和站点内相对路径。入库前后都应进行轻清洗，保留语义但避免制造长期校验噪声。

### 避免提交混入无关变更

知识入库任务通常产生多文件变更，必须用显式 staging 控制提交边界。若工作区已有其他修改，应只提交与本次知识资产闭环相关的文件。

### 避免过早全自动化

知识萃取需要理解项目语义，过早全自动化可能生成看似完整但不可用的 references 页面。当前更适合先标准化流程和校验，再逐步自动化机械环节。

## 与运行时闭环的关系

外部知识入库流水线是 Agent 系统运行时闭环的一种知识生产子流程。它将一次任务中的外部输入、工具执行、验证结果、复盘洞察和长期记忆连接起来。

```{mermaid}
flowchart LR
    A["外部知识"] --> B["sources 归档"]
    B --> C["references 萃取"]
    C --> D["索引与检索触发"]
    D --> E["后续任务调用"]
    E --> F["复盘与记忆"]
    F --> C
```

因此，这条流水线不仅是文档治理能力，也是 AgentForge 从静态知识库走向可演化工作系统的基础能力之一。

## Search Keywords

external knowledge ingestion, tutorial extraction pipeline, source to reference ingestion, 外部知识入库, 外部教程萃取, 知识资产流水线, sources references, manifest, raw source archive, structured extraction, Search Keywords, Trigger Phrases, linkcheck, 原子提交, 知识回流, AgentForge references, AgentForge sources, web content extraction, 文档站抓取, 真实源识别

## Trigger Phrases

- 如何把外部教程归档到 AgentForge？
- 外部 URL 如何转成 sources 和 references？
- 什么是 external-knowledge-ingestion？
- 如何设计外部知识入库流水线？
- 抓取教程时 sources 和 references 怎么分工？
- 外部文档入库需要生成 manifest 吗？
- 外部 Markdown 里的占位链接怎么处理？
- 如何判断外部知识入库是否完整？
- 如何把网页摘要变成项目知识资产？
- 外部知识入库如何做原子提交？
