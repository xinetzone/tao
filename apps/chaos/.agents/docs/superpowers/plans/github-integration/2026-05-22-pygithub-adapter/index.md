# PyGithub Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-22-pygithub-adapter.md，已原子化拆分

**Goal:** 为现有的 GitHub App 安装令牌管理器增加一个 `PyGithub` 薄适配层，方便业务使用对象化 API。

**Architecture:** 保留现有的 `httpx` 和 JWT 生成机制不变，在上方增加 `PyGithubInstallationClientFactory`，通过接收 `manager` 和 `settings`，获取到 token 后组装为 `github.Github` 对象并返回。

**Tech Stack:** Python 3.13+, `PyGithub`, `pytest`, `pytest-asyncio`

---

## 概述

本计划为现有的 GitHub App 安装令牌管理器增加一个 `PyGithub` 薄适配层，方便业务使用对象化 API。整体拆分为依赖更新、适配器实现、接口导出三个任务，各原子单元可独立阅读，便于按任务推进实现。

## 原子单元索引

| 单元名 | 主题 | 链接 |
|--------|------|------|
| Task 1: 更新依赖 | 添加 PyGithub 到可选依赖并通过导入测试 | [task-1-update-dependencies.md](task-1-update-dependencies.md) |
| Task 2: 实现 PyGithub 适配器 | 实现 `PyGithubInstallationClientFactory` 与 `build_pygithub_client` | [task-2-implement-pygithub-adapter.md](task-2-implement-pygithub-adapter.md) |
| Task 3: 在 `__init__.py` 暴露接口 | 导出适配器符号并扩展 `__all__` | [task-3-expose-interfaces.md](task-3-expose-interfaces.md) |
