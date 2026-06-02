# 可被 Agent 触发的知识资产

> 来源洞察：从 Hello-Agents 教程知识萃取任务中提炼出的 AgentForge 文档设计原则。
>
> 相关参考：[`external-knowledge-ingestion-pipeline.md`](./external-knowledge-ingestion-pipeline.md)、[`agent-runtime-closed-loop.md`](./agent-runtime-closed-loop.md)、[`agent-memory-dream-protocol.md`](./agent-memory-dream-protocol.md)、[`doc-maintenance-workflow.md`](./doc-maintenance-workflow.md)

## 定位

可被 Agent 触发的知识资产，是指不仅能被人类读懂，也能在后续 Agent 任务中被检索系统、上下文选择机制或 Agent 自身稳定召回的文档资产。

普通文档主要回答“人类读者读到这里能不能理解”。Agent 知识库还要额外回答“Agent 在什么时候会想起它、什么问题会触发它、它适合解决哪类任务、它和哪些来源或工作流相关”。

因此，面向 Agent 的稳定知识页必须同时写给两类读者：

| 读者 | 需要什么 | 文档设计重点 |
|---|---|---|
| 人类读者 | 清晰结构、背景解释、判断依据、示例 | 标题、章节、表格、流程、边界说明 |
| 检索系统和 Agent | 关键词、触发短语、适用场景、来源链接、任务意图 | Search Keywords、Trigger Phrases、When to Use、Related Tasks、Source Links |

如果只满足人类可读，文档可能写得很好，但未来 Agent 不一定能在正确任务中找到它。可触发性是 AgentForge 知识资产区别于普通 Markdown 文档的关键质量标准。

## 核心洞察

面向 Agent 的文档，必须同时写给“人类读者”和“检索系统”。

这意味着每个稳定知识页都应显式设计召回入口，而不是只在正文中自然出现相关词。正文负责解释，召回结构负责让知识在未来任务中被发现。

`Search Keywords` 和 `Trigger Phrases` 不是装饰，而是知识资产的触发接口。

## 为什么需要可触发性

Agent 执行任务时通常不会从头阅读整个知识库，而是依赖搜索、索引、规则、上下文路由或任务意图匹配找到少量相关页面。没有触发结构的页面会出现以下问题：

| 问题 | 表现 | 后果 |
|---|---|---|
| 标题弱语义 | 文件名或标题过于泛化 | 搜索时难以命中 |
| 关键词不足 | 正文只使用少量同义词 | 用户换一种说法就无法召回 |
| 触发短语缺失 | 页面没有覆盖自然语言问题 | Agent 不知道何时使用该页 |
| 适用范围不明 | 没有说明何时用、何时不用 | 容易误用或过度引用 |
| 来源链路不清 | 不知道知识从何而来 | 难以追溯和维护 |

Agent 知识库的目标不是“存了就行”，而是“在正确任务、正确时间、以正确粒度被召回”。

## 稳定知识页的触发结构

稳定知识页最好包含以下召回结构：

| 区块 | 作用 | 推荐内容 |
|---|---|---|
| Search Keywords | 覆盖检索词、英文术语、别名、错误短语 | 主关键词、同义词、英文名、常见缩写、相关框架名 |
| Trigger Phrases | 覆盖用户或 Agent 可能提出的问题 | “如何……”“什么时候……”“为什么……”这类自然语言触发句 |
| Related Tasks | 标明适合支撑哪些任务 | 调研、萃取、排障、设计、复盘、提交、迁移等 |
| When to Use | 明确使用条件 | 任务类型、问题阶段、输入形态、决策场景 |
| Source Links | 保留来源和相邻知识 | 原始资料、相关 references、rules、retrospectives、memories |

其中 `Search Keywords` 与 `Trigger Phrases` 是当前 AgentForge references 页面应优先具备的基础结构。`Related Tasks`、`When to Use` 和 `Source Links` 可在页面复杂度较高或任务复用价值较强时补充。

## Search Keywords 设计原则

`Search Keywords` 面向检索系统，重点是覆盖词面变化。

设计时应包含：

- 中文主关键词。
- 英文术语。
- 常见别名。
- 缩写。
- 相关工具、协议、框架名。
- 用户可能说错或说得不完整的短语。
- 与项目内部目录或概念相关的词。

示例：

```text
external knowledge ingestion, tutorial extraction pipeline, 外部知识入库, 外部教程萃取, sources references, manifest, Search Keywords, Trigger Phrases, linkcheck, 原子提交
```

关键词不需要写成句子，重点是让搜索能命中。对于跨语言项目，重要术语应中英文并列。

## Trigger Phrases 设计原则

`Trigger Phrases` 面向 Agent 的任务意图识别，重点是覆盖自然语言问题。

设计时应包含：

- 用户可能直接提出的问题。
- Agent 在执行中可能自问的问题。
- 与任务阶段相关的触发句。
- 与错误判断、放置位置、边界选择相关的触发句。

示例：

```text
- 如何把外部教程归档到 AgentForge？
- 外部 URL 如何转成 sources 和 references？
- 如何判断外部知识入库是否完整？
- 外部知识入库如何做原子提交？
```

触发短语应尽量像真实用户问题，而不是抽象标签。它们的价值在于帮助 Agent 将当前任务意图映射到可用知识页。

## Related Tasks 设计原则

`Related Tasks` 用于说明这篇知识页能支撑哪些任务类型，适合复杂参考页或流程页。

常见任务类型包括：

| 任务类型 | 示例 |
|---|---|
| 外部知识萃取 | 从教程、文档站、README 中抽取稳定知识 |
| 文档归档 | 判断资料应放入 sources、references、memories 还是 retrospectives |
| 架构设计 | 将外部知识映射到 AgentForge 概念、协议或运行时 |
| 复盘回流 | 从任务总结中提炼长期记忆或 references 页面 |
| 质量验证 | 检查链接、结构、关键词、触发短语和提交边界 |

`Related Tasks` 可以帮助 Agent 在计划阶段判断“这页是否与当前任务类型相关”。

## When to Use 设计原则

`When to Use` 用于控制召回后的使用边界。它回答“什么时候应该读这页，什么时候不应该读”。

推荐写法：

| 内容 | 说明 |
|---|---|
| 优先使用场景 | 明确最适合引用这页的任务 |
| 不适用场景 | 避免误用、过度泛化或扩大范围 |
| 前置条件 | 说明读这页前最好先知道什么 |
| 后续动作 | 说明读完后通常应执行什么 |

这能降低 Agent 误召回后的行动偏差。

## Source Links 设计原则

`Source Links` 用于支撑追溯和维护。它不只是外部 URL，也可以包括项目内部相邻知识资产。

可包含：

- 原始来源。
- 本地 sources 归档。
- 相关 references 页面。
- 相关 rules。
- 相关 retrospectives。
- 相关 memories。

对于外部知识入库任务，Source Links 尤其重要，因为它能把“原文是什么”“我们怎么理解”“后来如何回流”连接起来。

## 人类可读与 Agent 可触发的差异

| 维度 | 人类可读文档 | Agent 可触发知识资产 |
|---|---|---|
| 标题 | 能概括主题即可 | 必须包含主关键词，避免弱语义标题 |
| 结构 | 便于阅读 | 同时便于检索、切片和上下文选择 |
| 关键词 | 可自然出现在正文 | 需要集中列出，覆盖同义词和别名 |
| 触发方式 | 人主动打开 | Agent 通过任务意图或搜索召回 |
| 来源 | 可选 | 应尽量明确，便于追溯和维护 |
| 适用边界 | 可通过上下文理解 | 应显式写出，减少误用 |

一个简单判断标准是：如果把这篇文档交给一个没有当前对话上下文的 Agent，它能否根据用户问题判断“我应该读它”？如果不能，就说明可触发性不足。

## 写作检查清单

新增或维护 references 页面时，可以用以下清单检查：

| 检查项 | 判断问题 |
|---|---|
| 标题是否包含主关键词 | Agent 搜索标题时能否命中？ |
| 是否有 Search Keywords | 是否覆盖中文、英文、别名、缩写和相关术语？ |
| 是否有 Trigger Phrases | 是否覆盖真实用户问题和任务意图？ |
| 是否说明适用场景 | Agent 是否知道什么时候该用？ |
| 是否说明不适用场景 | Agent 是否知道什么时候不该用？ |
| 是否有来源或相关链接 | 未来能否追溯和更新？ |
| 是否与现有 references/rules 重复 | 是否需要合并、互链或调整边界？ |
| 是否能支撑下一步行动 | 读完后 Agent 是否知道该搜索、验证、归档还是提交？ |

## 与外部知识入库的关系

外部知识入库流水线负责把外部资料变成项目知识资产，可触发性负责让这些资产在未来任务中被召回。

```{mermaid}
flowchart LR
    A["外部资料"] --> B["sources 归档"]
    B --> C["references 萃取"]
    C --> D["Search Keywords"]
    C --> E["Trigger Phrases"]
    C --> F["When to Use"]
    D --> G["后续任务召回"]
    E --> G
    F --> G
    G --> H["Agent 执行"]
```

没有可触发性，外部知识入库只完成了“保存”；有了可触发性，知识资产才真正进入 Agent 工作流。

## 与知识操作系统的关系

AgentForge 的 `.agents/docs/` 可以被理解为知识操作系统：它持续吸收外部知识，重组为项目能力，再反哺 Agent 工作流。

在这个系统中，可触发知识资产相当于“可寻址模块”。每个稳定页面都应该有清晰主题、输入场景、触发短语和相邻链接。这样 Agent 才能在任务中像调用模块一样调用知识，而不是依赖偶然搜索。

这也是 `.agents/docs/` 区别于普通文档目录的核心：它不只保存知识，还要让知识可被任务触发、可被上下文路由、可被复盘回流、可被长期演化。

## Search Keywords

Agent triggerable knowledge assets, triggerable knowledge, Agent 可触发知识资产, Agent 知识库, Search Keywords, Trigger Phrases, Related Tasks, When to Use, Source Links, retrieval-friendly documentation, agent retrieval, knowledge recall, 召回结构, 检索系统, 知识资产召回, references 写作规范, AgentForge references, 人类读者, 检索系统, 知识操作系统

## Trigger Phrases

- 什么是可被 Agent 触发的知识资产？
- references 页面为什么要写 Search Keywords？
- Trigger Phrases 有什么作用？
- 如何让 Agent 在后续任务中想起某篇文档？
- 面向 Agent 的文档和普通文档有什么区别？
- 稳定知识页应该包含哪些召回结构？
- 如何提升 AgentForge 知识库的召回率？
- When to Use 和 Related Tasks 应该怎么写？
- `.agents/docs/` 为什么不只是文档目录？
- 如何把知识资产写给人类读者和检索系统？
