# constraints — 约束类记忆

> **维护责任人**：Leader Agent

## 模块功能

本模块存储项目中的技术约束与边界条件类记忆，主要覆盖 MyST Markdown、Sphinx、跨目录链接等工具链层面的限制与反例。

## 使用方法

- **何时查阅**：当你使用 MyST/Sphinx 构建文档、创建跨目录链接或遇到构建报错时
- **如何引用**：使用相对路径引用，如 `[MyST 跨目录链接边界约束](./2026-05-25-myst-cross-directory-link-constraint.md)`

## 依赖关系

- 被引用：[`../principles/`](../principles/README.md) 中的架构原则可能引用本模块约束作为设计边界

## 文件清单

| 文件 | 说明 |
|------|------|
| [2026-05-25-myst-cross-directory-link-constraint.md](./2026-05-25-myst-cross-directory-link-constraint.md) | MyST 跨目录链接边界约束与反例 |
