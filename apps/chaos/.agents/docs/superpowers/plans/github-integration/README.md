# github-integration — GitHub 集成计划

> **维护责任人**：Leader Agent

## 模块功能

本模块存储与 GitHub 集成相关的计划，包括 GitHub App 安装令牌覆盖机制与 PyGithub 适配器实现，为 GitHub API 调用提供认证、缓存、降级与适配层设计方案。

## 使用方法

- **何时查阅**：当你需要设计或调整 GitHub 认证机制、令牌管理、API 适配层时
- **如何引用**：使用相对路径引用，如 `[GitHub App 令牌覆盖计划](./2026-05-22-github-app-installation-token-override/index.md)`

## 依赖关系

- 引用外部：[`../python-environment/`](../python-environment/README.md) 中的环境管理为 GitHub 集成提供依赖与运行环境支撑
- 被引用：CI/CD 流水线与 CLI 诊断常引用本模块的令牌管理与适配层设计

## 文件清单

| 文件/目录 | 说明 |
|----------|------|
| [2026-05-22-github-app-installation-token-override/](./2026-05-22-github-app-installation-token-override/index.md) | GitHub App 安装令牌覆盖计划（原子化目录，含 6 个任务单元及自审、指标对比） |
| [2026-05-22-pygithub-adapter/](./2026-05-22-pygithub-adapter/index.md) | PyGithub 适配器实现计划（原子化目录，含 3 个任务单元） |
