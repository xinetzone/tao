# exploration — 探索任务计划

> **维护责任人**：Leader Agent

## 模块功能

本模块存储与探索任务相关的计划，包括 CLI 状态诊断、引用完整性检查、模板复用检查、知识驱动探索基础等，为探索性任务提供结构化的执行框架与验证记录。

## 使用方法

- **何时查阅**：当你需要开展探索性任务、设计探索协议、检查引用完整性或模板复用情况时
- **如何引用**：使用相对路径引用，如 `[知识驱动探索基础计划](./2026-05-24-knowledge-driven-exploration-foundation/index.md)`

## 依赖关系

- 引用外部：[`../agent-system/`](../agent-system/README.md) 中的协作元模型为探索任务提供角色边界约束
- 被引用：复盘报告常回流至 `../../retrospectives/` 中的对应模块

## 文件清单

| 文件/目录 | 说明 |
|----------|------|
| [2026-05-24-cli-status-diagnostics-exploration/](./2026-05-24-cli-status-diagnostics-exploration/index.md) | CLI 状态诊断探索计划（原子化目录，含探索检查与复盘） |
| [2026-05-24-exploration-reference-integrity-check/](./2026-05-24-exploration-reference-integrity-check/index.md) | 探索引用完整性检查计划（原子化目录，含检查记录与复盘） |
| [2026-05-24-exploration-template-reuse-check/](./2026-05-24-exploration-template-reuse-check/index.md) | 探索模板复用检查计划（原子化目录，含检查记录与复盘） |
| [2026-05-24-knowledge-driven-exploration-foundation/](./2026-05-24-knowledge-driven-exploration-foundation/index.md) | 知识驱动探索基础计划（原子化目录，含 6 个任务单元） |
