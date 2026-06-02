# DeepAgents Overview 教程萃取 Spec

## Why
LangChain DeepAgents overview 页面包含面向实践的深度智能体教程知识，需要被系统萃取为项目内可长期查阅的结构化知识资产，避免后续重复抓取和临时阅读。

## What Changes
- 抓取并研读 `https://docs.langchain.com/oss/python/deepagents/overview` 页面完整内容。
- 从页面教程类知识中提炼核心知识点、操作步骤、关键概念和实践案例。
- 按知识逻辑结构分类整理为清晰的中文 Markdown 知识文档。
- 根据项目文档治理规则，将萃取结果存储到合适的长期位置。
- 如目标目录存在索引或导航文件，按既有风格补充入口。
- 保留官方来源链接，不将 `.temp/` 临时抓取产物作为长期引用目标。

## Impact
- Affected specs: AI 参考资料沉淀、外部教程萃取、文档治理。
- Affected code: 预计不修改源码；主要影响 `apps/chaos/.agents/docs/` 下的 AI 知识库或参考资料目录，以及必要的索引文件。

## ADDED Requirements
### Requirement: DeepAgents overview 页面内容获取
The system SHALL retrieve the official DeepAgents overview page content and use it as the source for tutorial extraction.

#### Scenario: 获取官方页面
- **WHEN** 执行教程萃取任务
- **THEN** 应获取 `https://docs.langchain.com/oss/python/deepagents/overview` 的主要正文内容
- **AND** 临时抓取文件仅可放入 `.temp/`

### Requirement: 教程知识结构化萃取
The system SHALL transform the tutorial content into a structured Chinese knowledge document.

#### Scenario: 萃取核心要素
- **WHEN** 页面内容包含概念说明、步骤、示例或代码片段
- **THEN** 文档应提炼对应的核心知识点、关键概念、操作步骤和实践案例
- **AND** 内容应按逻辑结构分类整理，而不是简单复制原文

### Requirement: 长期归档位置合规
The system SHALL store the extracted tutorial in a project-appropriate long-term documentation location.

#### Scenario: 选择归档目录
- **WHEN** 判断内容属于面向 AI 智能体的外部技术参考资料
- **THEN** 应优先归档到 `apps/chaos/.agents/docs/references/` 或 `apps/chaos/.agents/docs/sources/` 下的合适位置
- **AND** 如存在索引文件，应按既有格式补充入口

### Requirement: 来源与引用合规
The system SHALL preserve the official source URL and avoid long-term references to local temporary artifacts.

#### Scenario: 写入持久化文档
- **WHEN** 生成最终知识文档
- **THEN** 文档应包含官方来源链接
- **AND** 不应链接 `.temp/` 中的抓取文件
- **AND** 项目内引用应使用相对路径，不得写入本地绝对路径或个人用户名路径

## MODIFIED Requirements
无。

## REMOVED Requirements
无。
