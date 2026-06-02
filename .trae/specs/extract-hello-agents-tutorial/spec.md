# Hello Agents 教程知识萃取 Spec

## Why
用户需要系统学习 `https://hello-agents.datawhale.cc/#/` 页面中的教程类知识，并将其萃取为项目内可长期查阅、可复用的结构化知识资产。该任务需要兼顾内容完整性、知识逻辑结构、项目文档边界和后续检索便利性。

## What Changes
- 抓取并阅读 `https://hello-agents.datawhale.cc/#/` 及其可访问教程内容。
- 对教程类知识进行系统性萃取，提炼核心知识点、操作步骤、关键概念和实践案例。
- 按知识逻辑结构分类整理为清晰的教程文档。
- 将整理后的教程内容存储到项目中合适的长期知识位置。
- 必要时更新对应目录索引，使后续能够通过项目文档导航查阅。
- 保留外部来源链接，避免把临时抓取产物作为长期引用来源。

## Impact
- Affected specs: 外部教程知识萃取、AI 参考资料沉淀、文档治理。
- Affected code: `apps/chaos/.agents/docs/` 或 `docs/general/` 下的合适文档位置，以及必要的索引文件。

## ADDED Requirements
### Requirement: 完整抓取教程内容
The system SHALL retrieve the tutorial content from `https://hello-agents.datawhale.cc/#/` and any directly linked tutorial pages required to understand the full tutorial structure.

#### Scenario: 成功获取教程结构
- **WHEN** 执行网页内容抓取和页面结构识别
- **THEN** 应获得教程的章节目录、主要页面内容和可用于萃取的原始文本

### Requirement: 系统性知识萃取
The system SHALL extract tutorial knowledge into structured categories including core concepts, key knowledge points, operation steps, practice cases, and learning sequence.

#### Scenario: 完成知识整理
- **WHEN** 对教程页面内容进行分析
- **THEN** 输出内容应按逻辑结构组织，而不是简单复制网页原文

### Requirement: 合规落盘到项目知识位置
The system SHALL store the extracted tutorial content in the project location that matches document governance rules and intended audience.

#### Scenario: 选择长期归档位置
- **WHEN** 判断教程内容面向 AI 智能体知识沉淀或通用学习资料
- **THEN** 应选择 `.agents/docs/` 或 `docs/general/` 下的合适位置，并遵循相应索引和引用规范

### Requirement: 可查阅与可验证
The system SHALL make the extracted content easy to find and verify by including source attribution, clear headings, and project-relative navigation where appropriate.

#### Scenario: 后续查阅
- **WHEN** 用户或智能体需要重新查阅 Hello Agents 教程萃取内容
- **THEN** 应能通过归档路径或目录索引快速定位，并确认内容来源
