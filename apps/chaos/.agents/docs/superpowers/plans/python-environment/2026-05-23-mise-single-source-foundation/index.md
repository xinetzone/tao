# mise Single Source Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-23-mise-single-source-foundation.md，已原子化拆分

**Goal:** 加固 AgentForge 的 mise 战略底座，使 `mise.toml` 成为工具层版本单一事实来源，并确保 `mise run init` / `mise run init-check` / `mise run check-env` 作为当前唯一推荐入口稳定可用。

**Architecture:** 采用低侵入方式修改现有环境校验脚本，不重构开发环境体系。`.agents/scripts/check_env.py` 负责从 `mise.toml` 解析工具层期望版本，并继续校验 Python 依赖层工具与配置一致性；文档只做入口口径收口。

**Tech Stack:** Python 3.14、标准库 `tomllib`、`pathlib.Path`、`dataclasses`、`subprocess`、mise、uv、Invoke、Markdown。

---

## 概述

本计划加固 AgentForge 的 mise 战略底座，使 `mise.toml` 成为工具层版本单一事实来源，并确保 `mise run init` / `mise run init-check` / `mise run check-env` 作为当前唯一推荐入口稳定可用。整体拆分为文件结构说明、环境校验脚本基础可运行性修复、从 `mise.toml` 读取工具层期望版本、收口当前推荐入口文档口径、端到端验证与收尾四个任务，并附带计划自查。各原子单元可独立阅读，便于按任务推进实现。

## 原子单元索引

| 单元名 | 主题 | 链接 |
|--------|------|------|
| File Structure | 文件结构、职责映射与共享约定 | [file-structure.md](file-structure.md) |
| Task 1: 修复环境校验脚本基础可运行性 | 补充必要导入并修正历史入口提示 | [task-1-fix-env-check-script.md](task-1-fix-env-check-script.md) |
| Task 2: 从 mise.toml 读取工具层期望版本 | TOML 读取与动态工具规格工厂 | [task-2-read-tool-versions-from-mise-toml.md](task-2-read-tool-versions-from-mise-toml.md) |
| Task 3: 收口当前推荐入口文档口径 | README/AGENTS/quickstart 入口统一 | [task-3-align-recommended-entrypoint-docs.md](task-3-align-recommended-entrypoint-docs.md) |
| Task 4: 端到端验证与收尾 | 环境校验、lint、语法检查与提交 | [task-4-end-to-end-verification-and-wrap-up.md](task-4-end-to-end-verification-and-wrap-up.md) |
| Plan Self-Review | 计划自查：Spec 覆盖、占位扫描、类型一致性 | [plan-self-review.md](plan-self-review.md) |
