# AI 开源库三库横向萃取分析 Spec

## Why
DeepAgents、LangGraph、LangChain 是 LangChain 生态下的三个核心 AI 开源库，分别定位为"厚夹具代理框架"、"状态化工作流引擎"、"基础抽象层"。它们之间存在紧密的技术继承与互补关系，但也各有独立的设计哲学。系统性地梳理三者的核心设计理念、功能模块、技术实现与适用场景，可为 AgentForge 项目的技术选型、架构设计和组件复用提供结构化参考。

## What Changes
- 对 `D:\spaces\AI\libs\deepagents`、`D:\spaces\AI\libs\langgraph`、`D:\spaces\AI\libs\langchain` 三个库进行系统性的源码级深度分析。
- 从核心设计理念、功能模块、关键实现逻辑、适用业务场景四个维度完成横向对比分析。
- 萃取各库核心技术亮点：状态管理机制、多智能体协作模式、工作流编排能力、工具调用框架、大模型集成方案等。
- 整理三库之间的技术关联、兼容性与互操作性，分析各自的优势与局限性。
- 输出结构化的萃取文档，包含架构图（Mermaid）、核心流程说明、代码示例提炼、场景适配建议。
- 基于萃取结果，总结可复用的技术组件与设计模式，形成可落地的技术参考手册。
- 按项目文档治理规则，将萃取结果归档到 `apps/chaos/.agents/docs/references/` 下的合适位置。

## Impact
- Affected specs: AI 参考资料沉淀、外部库技术萃取、文档治理。
- Affected code: 不修改源码；仅新增 `apps/chaos/.agents/docs/references/` 下的萃取文档。如存在索引文件，按既有格式补充入口。

## ADDED Requirements

### Requirement: 三库源码级深度分析
The system SHALL perform systematic source-code-level analysis of all three libraries based on locally available source code.

#### Scenario: 完成源码分析
- **WHEN** 执行三库分析任务
- **THEN** 应覆盖各库的核心模块源码、关键类定义、重要方法实现
- **AND** 分析应基于 `D:\spaces\AI\libs\` 下的实际源码，而非外部网络资源

### Requirement: 横向对比分析
The system SHALL produce a cross-comparison analysis covering core design philosophy, functional modules, key implementation logic, and applicable business scenarios for all three libraries.

#### Scenario: 完成横向对比
- **WHEN** 输出对比分析文档
- **THEN** 应包含三库在以下维度的结构化对比：
  - 核心设计理念与定位
  - 状态管理机制
  - 多智能体协作模式
  - 工作流编排能力
  - 工具调用框架
  - 大模型集成方案
  - 部署与运维能力
  - 优势与局限性

### Requirement: 技术关联与互操作性分析
The system SHALL analyze the technical relationships, compatibility, and interoperability among the three libraries.

#### Scenario: 技术关联梳理
- **WHEN** 分析三库技术关联
- **THEN** 应明确三库的继承/依赖关系（LangChain → LangGraph → DeepAgents）
- **AND** 说明各库在组合使用时的互操作模式
- **AND** 指出版本兼容性边界

### Requirement: 结构化萃取文档输出
The system SHALL produce structured extraction documents with architecture diagrams, core flow descriptions, code example extractions, and scenario adaptation recommendations.

#### Scenario: 文档完整性
- **WHEN** 输出最终萃取文档
- **THEN** 应包含：
  - 架构图（Mermaid 流程图/类图）
  - 核心流程说明（含序列图与时序描述）
  - 代码示例提炼（从实际源码中提取的关键模式）
  - 场景适配建议（何时选用哪个库/组合）
- **AND** 使用中文撰写

### Requirement: 可复用技术组件与设计模式总结
The system SHALL summarize reusable technical components and design patterns based on the extraction results, forming a practical technical reference manual.

#### Scenario: 设计模式提炼
- **WHEN** 完成萃取分析
- **THEN** 应提炼出可独立复用的设计模式（如中间件洋葱模型、Channel 更新策略、BSP 超级步模型等）
- **AND** 说明各模式在 AgentForge 项目中的潜在应用场景

### Requirement: 文档归档与索引合规
The system SHALL store the extraction documents in the project-appropriate long-term location following document governance rules.

#### Scenario: 文档落盘
- **WHEN** 生成最终文档
- **THEN** 应归档到 `apps/chaos/.agents/docs/references/` 下的合适子目录
- **AND** 如目标目录存在索引文件，按既有格式补充入口
- **AND** 项目内引用使用相对路径，不写入本地绝对路径

## MODIFIED Requirements
无。

## REMOVED Requirements
无。
