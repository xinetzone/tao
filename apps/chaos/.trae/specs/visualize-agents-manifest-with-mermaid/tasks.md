# Tasks
- [x] Task 1: 盘点 `AGENTS.md` 中适合图表化的现有内容并建立映射方案。
  - [x] SubTask 1.1: 标记文档中属于流程、架构、关系、职责映射、目录流转与时序交互的纯文字或表格内容。
  - [x] SubTask 1.2: 为每类内容选择最合适的 Mermaid 图表类型，明确哪些部分使用 `flowchart`、`classDiagram`、`sequenceDiagram` 或兼容 Markdown 的 C4 风格表达。
  - [x] SubTask 1.3: 确认哪些规则必须保留为文字约束，避免为了图表化而损失原始语义。

- [x] Task 2: 在 `AGENTS.md` 中新增 Mermaid 优先的规范规则。
  - [x] SubTask 2.1: 在规范章节加入“可视化逻辑内容优先使用 Mermaid”的明确约束。
  - [x] SubTask 2.2: 说明适用范围，包括流程、架构、关系、职责、层级与目录流转等内容。
  - [x] SubTask 2.3: 说明允许保留文字说明的例外条件与图文协同原则。

- [x] Task 3: 将现有可视化逻辑内容改写为 Mermaid 图表。
  - [x] SubTask 3.1: 使用流程图重构任务流转、上下文路由或其他步骤性说明。
  - [x] SubTask 3.2: 使用结构图重构角色职责关系、系统分层或目录边界说明。
  - [x] SubTask 3.3: 使用时序图重构多智能体协作或交互链路说明。
  - [x] SubTask 3.4: 保持原有核心业务规则、约束条件与章节逻辑不变，仅升级呈现形式。

- [x] Task 4: 校验 Mermaid 图表的语法、兼容性与文档整体质量。
  - [x] SubTask 4.1: 逐个检查新增 Mermaid 代码块的语法完整性与图表类型使用是否正确。
  - [x] SubTask 4.2: 按 GitHub、GitLab、Notion 等主流 Markdown 平台可接受的 Mermaid 语法子集排查兼容性问题。
  - [x] SubTask 4.3: 复核更新后的 `AGENTS.md` 是否图文一致、逻辑连贯、视觉清晰且符合技术文档专业写作标准。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
- [Task 4] depends on [Task 3]
