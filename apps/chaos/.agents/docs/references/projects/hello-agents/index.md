(hello-agents-reference)=
# Hello-Agents

> 来源项目：Datawhale China 的系统性智能体教程《从零开始构建智能体》
>
> 原始入口：`../../../sources/hello-agents/github-readme.md`
>
> 章节抓取：`../../../sources/hello-agents/chapters-manifest.json`
>
> 官方入口：<https://github.com/datawhalechina/hello-agents>、<https://datawhalechina.github.io/hello-agents/>

(hello-agents-positioning)=
## 定位

Hello-Agents 是面向 AI 开发者、软件工程师、在校学生和自学者的系统性 Agent 学习教程。它强调从基础理论到实际应用的完整路径，目标是让学习者从大语言模型的使用者转变为智能体系统构建者。

它明确区分两类 Agent 构建路线：

| 路线 | 代表 | 核心特征 |
|---|---|---|
| 软件工程类 Agent | Dify、Coze、n8n | 流程驱动的软件开发，LLM 作为数据处理后端 |
| AI Native Agent | 自研 Agent 框架、多智能体应用 | 以 AI 驱动为核心，从智能体循环、工具、记忆、协议到评估系统化构建 |

对 AgentForge 来说，Hello-Agents 的价值不只是“教程参考”，而是一个覆盖概念、范式、运行时能力、协议、评估与案例的外部知识样本，可用于校准 AgentForge 的 AI 文档组织、Agent 运行时抽象、协作协议与验证闭环。

(hello-agents-learning-path)=
## 学习路径

```{mermaid}
flowchart TD
    A["第一部分：智能体与语言模型基础"] --> B["第二部分：构建大语言模型智能体"]
    B --> C["第三部分：高级知识扩展"]
    C --> D["第四部分：综合案例进阶"]
    D --> E["第五部分：毕业设计及未来展望"]

    A --- A1["智能体定义、发展史、LLM 基础"]
    B --- B1["ReAct、Plan-and-Solve、Reflection、低代码平台、主流框架、自研框架"]
    C --- C1["记忆、RAG、上下文工程、通信协议、Agentic RL、性能评估"]
    D --- D1["旅行助手、深度研究智能体、赛博小镇"]
    E --- E1["完整多智能体应用与未来方向"]
```

(hello-agents-curriculum)=
## 课程结构萃取

| 部分 | 章节 | 主题 | 对 AgentForge 的参考价值 | 原始章节 |
|---|---|---|---|---|
| 智能体与语言模型基础 | 1-3 | 智能体定义、发展史、LLM 基础 | 补充 Agent 概念、范式与历史背景 | `01-introduction-to-agents.md`、`02-history-of-agents.md`、`03-fundamentals-of-large-language-models.md` |
| 构建大语言模型智能体 | 4-7 | ReAct、Plan-and-Solve、Reflection、低代码平台、主流框架、自研框架 | 对照 AgentForge 的执行循环、工具与框架边界 | `04-classic-agent-paradigms.md`、`05-low-code-agent-platforms.md`、`06-framework-development-practice.md`、`07-building-your-agent-framework.md` |
| 高级知识扩展 | 8-12 | 记忆、RAG、上下文工程、通信协议、Agentic RL、性能评估 | 补充记忆协议、上下文治理、评估体系与通信协议参考 | `08-memory-and-retrieval.md`、`09-context-engineering.md`、`10-agent-communication-protocols.md`、`11-agentic-rl.md`、`12-agent-performance-evaluation.md` |
| 综合案例进阶 | 13-15 | 智能旅行助手、自动化深度研究、赛博小镇 | 多智能体应用场景库与案例拆解来源 | `13-intelligent-travel-assistant.md`、`14-automated-deep-research-agent.md`、`15-building-cyber-town.md` |
| 毕业设计及未来展望 | 16 | 完整多智能体应用 | 任务分解、端到端项目设计与学习闭环参考 | `16-graduation-project.md` |

(hello-agents-chapter-index)=
## 已抓取章节索引

| 章节 | 本地原始文件 | 原始主题 | 主要内容 |
|---|---|---|---|
| 前言 | `../../../sources/hello-agents/00-preface.md` | 教程导言 | 课程目标、读者定位、学习方式 |
| 第 1 章 | `../../../sources/hello-agents/01-introduction-to-agents.md` | 初识智能体 | Agent 定义、智能体与工作流差异、AI Agent 入门心智模型 |
| 第 2 章 | `../../../sources/hello-agents/02-history-of-agents.md` | 智能体发展史 | 从早期 AI、符号主义、强化学习到 LLM Agent 的演进 |
| 第 3 章 | `../../../sources/hello-agents/03-fundamentals-of-large-language-models.md` | 大语言模型基础 | Transformer、预训练、后训练、推理、LLM API 调用基础 |
| 第 4 章 | `../../../sources/hello-agents/04-classic-agent-paradigms.md` | 智能体经典范式构建 | ReAct、Plan-and-Solve、Reflection 等范式与实现 |
| 第 5 章 | `../../../sources/hello-agents/05-low-code-agent-platforms.md` | 低代码平台搭建 | Dify、Coze、n8n 等平台化 Agent 构建路线 |
| 第 6 章 | `../../../sources/hello-agents/06-framework-development-practice.md` | 框架开发实践 | LangChain、AutoGen、CAMEL、MetaGPT 等框架实践 |
| 第 7 章 | `../../../sources/hello-agents/07-building-your-agent-framework.md` | 构建 Agent 框架 | HelloAgents 框架、LLM 抽象、工具系统、Agent 执行循环 |
| 第 8 章 | `../../../sources/hello-agents/08-memory-and-retrieval.md` | 记忆与检索 | 短期记忆、长期记忆、RAG、MemoryTool、检索增强 |
| 第 9 章 | `../../../sources/hello-agents/09-context-engineering.md` | 上下文工程 | GSSC 流水线、ContextBuilder、NoteTool、TerminalTool、上下文预算 |
| 第 10 章 | `../../../sources/hello-agents/10-agent-communication-protocols.md` | 智能体通信协议 | MCP、A2A、ANP、协议工具封装、服务发现与协作 |
| 第 11 章 | `../../../sources/hello-agents/11-agentic-rl.md` | Agentic-RL | 强化学习基础、Agent 训练、ToolRL、GRPO、MCPWorld |
| 第 12 章 | `../../../sources/hello-agents/12-agent-performance-evaluation.md` | 智能体性能评估 | BFCL、GAIA、数据生成质量评估、LLM Judge、Win Rate |
| 第 13 章 | `../../../sources/hello-agents/13-intelligent-travel-assistant.md` | 智能旅行助手 | 需求分析、工具集成、个性化行程规划应用 |
| 第 14 章 | `../../../sources/hello-agents/14-automated-deep-research-agent.md` | 自动化深度研究智能体 | 研究任务分解、信息检索、报告生成、深度研究链路 |
| 第 15 章 | `../../../sources/hello-agents/15-building-cyber-town.md` | 构建赛博小镇 | 多智能体仿真、角色设定、社交交互、虚拟社区 |
| 第 16 章 | `../../../sources/hello-agents/16-graduation-project.md` | 毕业设计 | 综合项目、能力整合、未来展望 |

(hello-agents-core-concepts)=
## 核心概念萃取

| 概念 | Hello-Agents 中的含义 | 可迁移到 AgentForge 的机制 |
|---|---|---|
| Agent | 具备感知、决策、行动与反馈循环的智能系统，不只是单轮 LLM 调用 | 将 Agent 定义为运行时实体，明确输入、状态、工具、输出与反馈边界 |
| AI Native Agent | 以 LLM 推理和工具调用为中心构建的智能体，而非仅把 LLM 嵌入传统工作流 | 强化 AgentForge 对“协议 + 运行时 + 知识资产”的整体抽象 |
| Agent Loop | 任务输入后，模型在观察、思考、行动、反馈中循环推进 | 可映射到任务执行器、工具调用、上下文压缩、状态持久化 |
| Tool System | 把外部能力封装为可由 Agent 调用的统一接口 | 可参考工具注册、工具说明、工具边界与错误恢复机制 |
| Memory / RAG | 将历史、外部知识和任务状态从上下文窗口外部按需召回 | 对应 AgentForge 的知识库、长期记忆、检索、做梦重组与回流机制 |
| Context Engineering | 在每次模型调用前，以工程化方式拼装、筛选、结构化、压缩上下文 | 对应上下文节省、路由、文档分层、任务中间产物与压缩摘要规则 |
| Communication Protocol | 让 Agent 与工具、Agent 与 Agent、Agent 与网络以标准方式通信 | 对应协作元模型、Team/Role/Agent、MCP/A2A/ANP 借鉴方向 |
| Agentic RL | 用强化学习方法优化 Agent 的多步决策、工具调用和环境交互能力 | 可作为未来自进化、反馈闭环、策略优化的参考材料 |
| Evaluation System | 通过基准、指标和评测工具客观衡量 Agent 能力 | 对应验证机制、测试门禁、任务完成质量和智能体评估闭环 |
| Multi-Agent Application | 多个专业角色协作完成复杂任务或构成仿真世界 | 对应 AgentForge 的协作协议、角色编排和世界运行时设计 |

(hello-agents-build-steps)=
## 从零构建 Agent 的步骤模型

Hello-Agents 的章节组织可以萃取为一个递进式构建流程：

```{mermaid}
flowchart LR
    S1["明确 Agent 问题与边界"] --> S2["选择 LLM 与提示结构"]
    S2 --> S3["实现经典推理范式"]
    S3 --> S4["接入工具系统"]
    S4 --> S5["加入记忆与检索"]
    S5 --> S6["治理上下文"]
    S6 --> S7["接入协议与多 Agent 协作"]
    S7 --> S8["评估、优化与案例落地"]
```

| 步骤 | 关键问题 | Hello-Agents 参考章节 | AgentForge 萃取方向 |
|---|---|---|---|
| 1. 明确 Agent 问题与边界 | 任务是否需要自主规划、工具调用、记忆或多轮反馈？ | 第 1-2 章 | 区分“普通自动化”“工作流”“Agent Runtime” |
| 2. 选择 LLM 与提示结构 | 模型能力、系统提示、输出格式、错误恢复如何设计？ | 第 3 章 | 建立 LLM 调用抽象和提示模板规范 |
| 3. 实现经典推理范式 | 使用 ReAct、Plan-and-Solve、Reflection 中哪种控制策略？ | 第 4 章 | 对照任务执行器的规划、行动、反思边界 |
| 4. 接入工具系统 | 工具如何描述、注册、调用、处理错误？ | 第 4、7 章 | 工具元数据、工具协议、最小可行工具集 |
| 5. 加入记忆与检索 | 哪些状态进入短期上下文，哪些沉入长期记忆？ | 第 8 章 | 记忆分层、检索策略、知识资产回流 |
| 6. 治理上下文 | 如何在 token 预算内保留高价值信息？ | 第 9 章 | Gather-Select-Structure-Compress、上下文预算、渐进披露 |
| 7. 接入协议与多 Agent 协作 | 工具、Agent、网络之间如何互操作？ | 第 10、15 章 | MCP/A2A/ANP、角色编排、协议边界 |
| 8. 评估与优化 | 如何证明 Agent 变好了？ | 第 11-12 章 | 基准、指标、LLM Judge、回归测试、自进化闭环 |
| 9. 案例落地 | 如何把能力组合成端到端应用？ | 第 13-16 章 | 场景卡、应用架构、交付验收标准 |

(hello-agents-paradigms)=
## 智能体范式萃取

| 范式 | 解决的问题 | 典型流程 | 适用场景 | 注意事项 |
|---|---|---|---|---|
| ReAct | 让模型交替推理与行动 | Thought → Action → Observation → Answer | 搜索、工具调用、多步信息获取 | 工具输出要短而准，避免循环发散 |
| Plan-and-Solve | 先制定计划，再按步骤解决 | Plan → Execute Steps → Final Answer | 复杂任务拆解、研究、代码实现 | 计划需要可更新，不能僵化执行旧计划 |
| Reflection | 让模型评估并修正自身输出 | Draft → Critique → Revise | 代码生成、写作、推理校正 | 反思标准要具体，否则容易空泛自证 |
| Tool-Using Agent | 将外部 API、文件、搜索等能力纳入循环 | Intent → Tool Selection → Invocation → Result Integration | 需要外部信息或行动的任务 | 工具边界清晰比工具数量更重要 |
| Multi-Agent | 多角色协作分工 | Coordinator → Specialist Agents → Merge | 研究、模拟、复杂项目 | 需要上下文隔离、角色契约和结果汇总机制 |

(hello-agents-context-engineering)=
## 上下文工程萃取

第九章把上下文工程定义为：在每一次 LLM 调用前，以可复用、可度量、可演进的方式拼装并优化输入上下文。其核心不是写更长的 prompt，而是管理整个上下文状态。

### GSSC 流水线

| 阶段 | 目标 | 典型输入 | 典型输出 | AgentForge 对应做法 |
|---|---|---|---|---|
| Gather | 收集候选信息 | 系统提示、任务、历史消息、文件、检索结果、工具输出 | ContextPacket 候选集 | 先搜索、再精读；按路由读取相关 AGENTS/rules/docs |
| Select | 按相关性、新近性和预算选择 | 候选上下文包、token 预算 | 高价值上下文子集 | 上下文节省规则、最小必要信息集 |
| Structure | 固定骨架组织上下文 | 角色、任务、状态、证据、历史、输出要求 | 稳定上下文模板 | 文档分层、固定章节、可检索关键词 |
| Compress | 超限时高保真压缩 | 历史对话、工具输出、阶段结果 | 摘要、结构化笔记、任务状态 | `.temp/` 中间产物、长期记忆、复盘回流 |

### 可迁移原则

- 上下文是有限资源，越长不等于越好。
- 系统提示、工具描述、示例、历史消息和外部资料都属于上下文工程的一部分。
- 长任务需要压缩整合、结构化笔记和子代理隔离，而不是无限追加聊天历史。
- 运行时检索应倾向渐进式披露：先给路径、索引和高价值摘要，再按需读取原文。
- 工具返回值应 token 友好，避免把低价值噪声放入模型工作记忆。

(hello-agents-protocols)=
## 通信协议萃取

第十章把智能体通信协议分为三类：

| 协议 | 通信对象 | 核心用途 | 设计关键词 | AgentForge 可借鉴点 |
|---|---|---|---|---|
| MCP | Agent ↔ Tool / Resource | 标准化工具、资源和上下文访问 | 上下文共享、工具发现、统一接口 | 外部工具接入、文件/数据库/API 资源协议化 |
| A2A | Agent ↔ Agent | 点对点智能体协作 | 对等通信、任务委派、消息协商 | Team/Role/Agent 协作、角色间任务传递 |
| ANP | Agent ↔ Agent Network | 大规模网络中的服务发现与连接 | 去中心化发现、注册、路由 | 跨项目智能体目录、能力市场、世界级运行时 |

协议选择可遵循简单判断：

| 需求 | 优先协议 |
|---|---|
| 访问文件、数据库、GitHub、Slack 等外部服务 | MCP |
| 让研究员、撰写员、编辑等多个 Agent 协同工作 | A2A |
| 构建可发现、可路由、可扩展的 Agent 网络 | ANP |

(hello-agents-evaluation)=
## 评估体系萃取

第十二章强调：没有评估就无法证明 Agent 的优化有效。智能体评估与传统软件测试不同，因为输出具有不确定性、标准多样、成本较高。

| 评估方向 | 基准或方法 | 评估能力 | 可用于 AgentForge 的场景 |
|---|---|---|---|
| 工具调用能力 | BFCL、ToolBench、API-Bank | 函数选择、参数构造、无关调用拒绝 | 检查工具说明是否清晰、调用是否稳定 |
| 通用助手能力 | GAIA、AgentBench、WebArena | 多步推理、网页/文件处理、复杂任务完成 | 验证复杂任务执行器、研究工作流和文件操作能力 |
| 多智能体协作 | ChatEval、SOTOPIA、自定义场景 | 角色协作、沟通效率、任务完成度 | 验证 Team/Role/Agent 协作协议 |
| 生成质量 | LLM Judge、Win Rate、人工验证 | 答案质量、数据质量、报告质量 | 文档萃取、报告生成、知识回流质量评估 |
| 效率与鲁棒性 | 响应时间、token 使用量、错误率、恢复率 | 成本、延迟、容错能力 | CI 验证、回归检查、上下文预算治理 |

可迁移为 AgentForge 的验证闭环：

```{mermaid}
flowchart LR
    A["定义能力与场景"] --> B["准备任务集与期望标准"]
    B --> C["运行 Agent / Workflow"]
    C --> D["采集输出、工具调用、token 与错误"]
    D --> E["指标评估或 LLM Judge"]
    E --> F["定位失败模式"]
    F --> G["修改提示、工具、上下文或协议"]
    G --> C
```

(hello-agents-cases)=
## 案例萃取

| 案例 | 对应章节 | 能力组合 | 可复用模式 | AgentForge 可借鉴点 |
|---|---|---|---|---|
| 智能旅行助手 | 第 13 章 | 用户偏好理解、地点/天气/交通查询、计划生成 | 个性化规划 Agent | 场景卡、约束收集、工具组合、结果格式化 |
| 自动化深度研究智能体 | 第 14 章 | 问题拆解、资料搜索、证据整理、报告生成 | Research → Evidence → Report | 文档萃取、引用追溯、子任务并行、报告模板 |
| 赛博小镇 | 第 15 章 | 多角色设定、互动规则、状态演化、仿真世界 | Multi-Agent Simulation | Team/Role/Agent 元模型、世界状态、事件循环 |
| 毕业设计 | 第 16 章 | 综合使用框架、工具、记忆、协议、评估 | 端到端项目交付 | 从教程到项目的验收清单与交付路径 |

(hello-agents-agentforge-mapping)=
## 与 AgentForge Spec v0.2 的映射

| Hello-Agents 内容 | AgentForge Spec v0.2 层级 | 可萃取方向 |
|---|---|---|
| 教程项目 README、章节导航、学习路径 | Layer 1 Project Protocol | 项目级 AI 知识资产的索引与导航组织方式 |
| 智能体通信协议、多智能体案例 | Layer 2 Collaboration Protocol | Team/Role/Agent、协议协作、任务分解、上下文隔离 |
| 记忆、上下文工程、Agentic RL、自进化内容 | Layer 3 World Runtime | 记忆循环、反馈闭环、运行时优化与世界特定能力 |
| 自研 HelloAgents 框架 | Layer 2 / Layer 3 交界 | Agent 执行循环、工具注册、框架扩展点、评估闭环 |
| 深度研究与旅行助手案例 | Layer 1 / Layer 2 交界 | 应用场景卡、任务约束收集、交付验收结构 |
| 性能评估系统 | 横跨三层 | 将能力定义、任务集、指标、回归验证接入项目治理 |

(hello-agents-reference-playbook)=
## AgentForge 使用建议

当需要借鉴 Hello-Agents 时，建议按任务类型读取：

| 任务 | 先读萃取页 | 再追溯原文 |
|---|---|---|
| 解释 Agent 基础概念 | 本页“核心概念萃取” | 第 1-3 章原始抓取 |
| 设计 Agent 执行循环 | 本页“智能体范式萃取” | 第 4、7 章原始抓取 |
| 设计上下文管理策略 | 本页“上下文工程萃取” | 第 9 章原始抓取 |
| 设计多 Agent 协作协议 | 本页“通信协议萃取” | 第 10、15 章原始抓取 |
| 设计评估和验证机制 | 本页“评估体系萃取” | 第 12 章原始抓取 |
| 寻找应用案例 | 本页“案例萃取” | 第 13-16 章原始抓取 |

(hello-agents-core-takeaways)=
## 核心要点

- 教程采用“理论基础 → 单智能体构建 → 高级能力 → 综合案例 → 毕业设计”的递进结构。
- 学习目标不是仅使用平台，而是理解智能体核心架构并动手构建 AI Native Agent。
- 第二部分从经典范式与主流框架过渡到自研 HelloAgents 框架，强调“用轮子”和“造轮子”并重。
- 第三部分覆盖记忆、检索、上下文工程、通信协议、Agentic RL 和性能评估，适合与 AgentForge 的记忆、上下文、协议和验证机制交叉参考。
- 第四部分提供旅行助手、DeepResearch、赛博小镇等案例，可作为多智能体协作与应用落地的场景素材。
- 对 AgentForge 来说，最值得优先迁移的是上下文工程 GSSC、通信协议分层、评估闭环和多智能体案例拆解方法。

(hello-agents-follow-up)=
## 后续可深入萃取方向

| 优先级 | 章节或资料 | 目的 |
|---|---|---|
| 高 | 第九章 上下文工程 | 对照 AgentForge 的上下文节省、路由与知识检索规则，形成独立参考页 |
| 高 | 第十章 智能体通信协议 | 补充 MCP、A2A、ANP 与协作元模型参考，形成协议对照表 |
| 高 | 第十二章 智能体性能评估 | 为 AgentForge 验证与评估体系提供指标参考，形成评估 playbook |
| 中 | 第七章 构建你的 Agent 框架 | 对照 world CLI、工具注册与 Agent 运行时边界 |
| 中 | 第十三至十五章综合案例 | 沉淀多智能体场景卡与应用架构模式 |
| 中 | Extra-Chapter 的 Skill、WebAgent、自进化内容 | 补充技能生态、Web Agent 与自我演化经验 |

(hello-agents-search-keywords)=
## Search Keywords

Hello-Agents, Hello Agents, Datawhale, 从零开始构建智能体, AI Native Agent, ReAct, Plan-and-Solve, Reflection, Tool System, Memory, RAG, Context Engineering, GSSC, ContextBuilder, MCP, A2A, ANP, Agentic RL, BFCL, GAIA, LLM Judge, Win Rate, DeepResearch Agent, 赛博小镇, 智能旅行助手, 多智能体教程

(hello-agents-trigger-phrases)=
## Trigger Phrases

- “查一下 Hello-Agents 教程结构”
- “智能体从零学习路线是什么”
- “AgentForge 可以借鉴 Hello-Agents 哪些内容”
- “找一个系统性 Agent 教程作为参考”
- “多智能体案例有哪些可学习项目”
- “Hello-Agents 的上下文工程怎么做”
- “MCP、A2A、ANP 有什么区别”
- “Agent 评估体系怎么设计”
- “DeepResearch Agent 案例可以怎么拆解”
