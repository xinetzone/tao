# `AGENTS.md` Mermaid 可视化规范升级 Spec

## Why
当前 `AGENTS.md` 已经清晰定义了 AI 智能体的全局契约、上下文路由与文档边界，但其中涉及流程、职责映射、目录关系与体系结构的内容仍主要以纯文字和表格表达为主，阅读时需要开发者自行在脑中重建结构。
将这些可视化逻辑统一升级为 Markdown 原生支持的 Mermaid 图表，可以在不改变业务语义的前提下显著提升可读性、维护效率与跨平台知识传递效果。

## What Changes
- 在 `AGENTS.md` 的规范章节中新增“Mermaid 优先”的文档编写规则，要求后续维护者对可视化逻辑内容优先采用 Mermaid 语法表达。
- 盘点 `AGENTS.md` 中现有的纯文字流程、角色职责关系、系统分层与信息流转内容，并替换为语义匹配的 Mermaid 图表。
- 对不同类型的信息采用合适的 Mermaid 图表类型，例如 `flowchart`、`sequenceDiagram`、`classDiagram` 与兼容 Markdown 的 C4 风格架构图表达。
- 保留 `AGENTS.md` 原有核心规则、约束与业务语义，仅优化其呈现形式、章节组织与可视化表达方式。
- 对新增图表进行语法与兼容性校验，确保其能被 GitHub、GitLab、Notion 等主流 Markdown 编辑环境稳定渲染，或至少以兼容子集形式优雅降级。

## Impact
- Affected specs: AI 契约文档规范、文档可视化表达、智能体职责说明、任务流转说明
- Affected code: `AGENTS.md`

## ADDED Requirements
### Requirement: `AGENTS.md` 的 Mermaid 优先可视化规则
系统 SHALL 在 `AGENTS.md` 的规范章节中明确规定：凡属于流程、架构、关系、职责映射、目录流转、时序交互等可视化逻辑内容，后续维护时必须优先使用 Mermaid 语法表达，而不是继续扩写为大段纯文字说明。

#### Scenario: 维护者新增流程说明
- **WHEN** 维护者需要在 `AGENTS.md` 中新增任务流转、上下文路由或执行链路说明
- **THEN** 应优先使用 Mermaid 图表表达流程逻辑
- **THEN** 仅对图中无法自解释的规则补充必要文字说明

#### Scenario: 维护者新增结构关系说明
- **WHEN** 维护者需要描述角色继承、模块关联、系统分层或文档目录关系
- **THEN** 应优先选用匹配的 Mermaid 图表类型表达结构关系
- **THEN** 不再以纯文字堆叠方式重复图中已经清晰表达的信息

### Requirement: 现有可视化内容的图表化替换
系统 SHALL 梳理 `AGENTS.md` 中现有的纯文字流程逻辑、角色职责关联、系统架构分层、信息流转链路与目录关系，并将这些内容替换为对应的 Mermaid 图表，且替换后保留原有业务语义与约束边界。

#### Scenario: 流程内容改写为流程图
- **WHEN** 文档中存在任务执行顺序、上下文路由或目录流转等步骤性描述
- **THEN** 这些内容使用 `flowchart` 或等效 Mermaid 流程图语法表达
- **THEN** 图中节点与连线能够完整覆盖原有步骤关系

#### Scenario: 关系内容改写为结构图
- **WHEN** 文档中存在智能体角色职责关联、文档层级关系或系统组成关系
- **THEN** 这些内容使用 `classDiagram`、兼容的 C4 风格 Mermaid 语法或其他更适配的 Mermaid 图表类型表达
- **THEN** 图表表达不改变原有职责归属、层级边界与依赖方向

### Requirement: 主流 Markdown 渲染兼容性
系统 SHALL 对 `AGENTS.md` 中新增的 Mermaid 图表使用主流 Markdown 编辑器可接受的语法子集，并在交付前完成渲染兼容性检查，避免出现平台常见的不兼容写法、未闭合块、非法标识符或依赖私有扩展的语法。

#### Scenario: 在 GitHub 或 GitLab 中渲染
- **WHEN** 维护者将更新后的 `AGENTS.md` 提交到支持 Mermaid 的代码托管平台
- **THEN** 文档中的 Mermaid 代码块能够被平台识别为标准 Mermaid 图表
- **THEN** 图表不存在导致整体渲染失败的语法错误

#### Scenario: 在 Notion 或其他 Markdown 编辑器中查看
- **WHEN** 维护者将文档复制或同步到支持 Mermaid 的第三方编辑器
- **THEN** 图表语法保持在通用 Mermaid 能力范围内
- **THEN** 即便存在平台差异，图表结构与文本说明仍保持可读和可维护

## MODIFIED Requirements
### Requirement: `AGENTS.md` 的规范表达方式
`AGENTS.md` 现有的规范表达方式必须从“以文字和表格为主、由读者自行推导结构”升级为“以 Mermaid 图表承载流程、架构、关系等可视化内容，辅以必要的精炼文字说明”的表达方式。

### Requirement: `AGENTS.md` 的可读性标准
`AGENTS.md` 的可读性标准必须从“逻辑完整即可”升级为“逻辑完整、图文一致、视觉层次清晰且能在主流 Markdown 编辑器中稳定渲染”。

## REMOVED Requirements
### Requirement: 无
**Reason**: 本次变更只优化 `AGENTS.md` 的表达形式与维护规则，不移除任何既有业务规则或执行约束。
**Migration**: 现有纯文字说明中的可视化信息迁移为 Mermaid 图表，无法图示化的补充说明继续保留为精炼文本。
