# 外部知识入库应转化为项目语义资产

## Type

原则 / 经验

## Scope

- 适用项目：AgentForge 及任何具备 AI 知识库、长期文档资产、外部资料沉淀需求的项目
- 适用场景：从外部教程、官方文档、课程资料、开源项目 README 或文档站中萃取知识，并归档为项目内长期资产
- 不适用场景：一次性网页摘要、临时调研笔记、无需长期维护或无需被 Agent 检索复用的资料

## Content

- 记忆内容：
  - 外部教程不应只被当作链接或摘要保存，而应转化为项目语义资产。
  - 高质量外部知识入库至少包含三层：
    - `sources/`：保留原始资料、章节清单、来源链接和追溯信息，回答“原文是什么”。
    - `references/`：按本项目语义重组后的稳定知识页，回答“这对我们意味着什么”。
    - 索引入口：将知识接入现有导航和检索体系，回答“以后怎么找到它”。
  - “全部内容”不等于全文复制。完整性应通过目录覆盖、核心概念、操作步骤、关键案例、来源追溯和验证闭环共同保证。
  - 对文档站、教程站或 GitHub Pages 镜像，应优先识别真实源，例如 GitHub 仓库 Markdown，而不是只抓取入口网页。
  - 外部 Markdown 进入长期文档库前需要轻清洗：占位链接、示例 URL、本地路径、个人用户名路径和无效链接不应污染项目链接检查。
  - 面向 Agent 的稳定知识页应包含 `Search Keywords` 和 `Trigger Phrases`，让知识不仅可读，而且可被后续任务检索和触发。

- 为什么值得记忆：
  - 本次 Hello-Agents 教程萃取证明，外部知识的长期价值不在于“保存资料”，而在于通过项目语义重构、索引接入和验证闭环，使其成为可被人类和 Agent 共同复用的知识资产。
  - 该原则可迁移到未来任何外部教程入库任务，例如框架教程、协议文档、工具链资料、课程笔记和开源项目知识萃取。

- 它未来能降低什么成本：
  - 降低抓取成本：先识别真实源，再批量获取目录和章节。
  - 降低理解成本：通过稳定萃取页避免每次重新阅读全量原文。
  - 降低检索成本：通过索引、关键词和触发短语提升 Agent 召回率。
  - 降低维护成本：通过 sources / references 分层避免原文追溯与项目语义混杂。
  - 降低验证成本：通过链接检查和轻清洗减少长期文档库中的死链和占位链接。

## Source

- 来源类型：复盘 / 实施 / 用户偏好
- 来源位置：`.agents/docs/superpowers/retrospectives/task-summary-hello-agents-knowledge-extraction-20260602.md`
- 相关提交：`4b8fc31 docs(agents): extract hello-agents tutorial knowledge`、`7514d2a docs(retrospective): summarize hello-agents extraction task`
- 形成日期：2026-06-02

## Expiration Conditions

- 何时可能过期：当项目引入自动化知识入库系统，能够自动完成真实源识别、抓取、清洗、萃取、索引和验证时
- 何时需要复查：新增 `external-knowledge-ingestion`、`tutorial-extraction-pipeline` 或类似工作流 / skill 时
- 哪些变化会使它失效：如果 `.agents/docs/` 不再采用 `sources/`、`references/`、`superpowers/` 分层，或项目文档治理规则发生根本变化

## Feedback Suggestion

- 建议回流位置：工作流 / 参考页 / 规则
- 回流理由：该洞察已超出 Hello-Agents 单次任务，可固化为外部教程知识入库的标准流程或 skill
- 是否需要做梦重组：是
