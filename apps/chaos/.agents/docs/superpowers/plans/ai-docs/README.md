# ai-docs — AI 文档系统计划

> **维护责任人**：Leader Agent

## 模块功能

本模块存储与 AI 文档系统构建相关的计划，包括 AI 参考维基搭建、文档导航设计、搜索关键词策略等，旨在为 AI 智能体提供结构化的参考知识库与检索入口。

## 使用方法

- **何时查阅**：当你需要规划或扩展 AI 文档系统、设计导航结构、配置搜索关键词时
- **如何引用**：使用相对路径引用，如 `[AI 参考维基计划](./2026-05-22-ai-reference-wiki/index.md)`

## 依赖关系

- 引用外部：[`../docs-governance/`](../docs-governance/README.md) 中的文档治理框架为 AI 文档系统提供治理依据
- 被引用：[`../agent-system/`](../agent-system/README.md) 中的智能体协作元模型常引用本模块的参考维基作为知识源

## 文件清单

| 文件/目录 | 说明 |
|----------|------|
| [2026-05-22-ai-docs-navigation.md](./2026-05-22-ai-docs-navigation.md) | AI 文档导航结构设计计划 |
| [2026-05-22-ai-docs-search-keywords.md](./2026-05-22-ai-docs-search-keywords.md) | AI 文档搜索关键词策略计划 |
| [2026-05-22-ai-reference-wiki/](./2026-05-22-ai-reference-wiki/index.md) | AI 参考维基搭建计划（原子化目录，含 5 个任务单元） |
