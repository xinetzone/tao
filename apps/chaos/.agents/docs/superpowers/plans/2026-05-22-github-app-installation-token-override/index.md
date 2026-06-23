# GitHub App Installation Token Override Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-22-github-app-installation-token-override.md，已原子化拆分

**Goal:** 为 `AgentForge` 新增兼容 GitHub.com / GHEC 与 GHES 的 GitHub App 安装令牌管理层，支持请求级覆盖头、缓存、单飞刷新、CLI、学习笔记与测试报告。

**Architecture:** 采用“配置解析 + HTTP 客户端 + 进程内缓存 + 令牌编排器 + CLI”五层结构。令牌格式一律按 opaque secret 处理，`auto / enabled / disabled` 策略与环境降级逻辑统一收敛在 `token_manager` 与 `client`，通过 `httpx.MockTransport` 驱动功能测试与并发压测。

**Tech Stack:** Python 3.13+, `httpx`, `PyJWT[crypto]`, `pytest`, `pytest-asyncio`, `uv`, GitHub Actions

---

## 概述

本计划为 `AgentForge` 新增兼容 GitHub.com / GHEC 与 GHES 的 GitHub App 安装令牌管理层。整体拆分为配置层、GitHub 客户端、缓存与令牌编排器、单飞刷新与压测、CLI 双入口、文档与 CI 验证六个任务，并附带指标对比与计划自查。各原子单元可独立阅读，便于按任务推进实现。

## 原子单元索引

| 单元名 | 主题 | 链接 |
|--------|------|------|
| File Structure | 文件结构、职责映射与共享约定 | [file-structure.md](file-structure.md) |
| Task 1: 建立配置层与基础模型 | 配置解析、环境识别与基础模型 | [task-1-config-layer.md](task-1-config-layer.md) |
| Task 2: 实现 GitHub 客户端与请求头覆盖逻辑 | 客户端、JWT 签发与覆盖头 | [task-2-github-client.md](task-2-github-client.md) |
| Task 3: 实现缓存与令牌编排器的基础路径 | 进程内缓存与令牌编排器 | [task-3-cache-token-manager.md](task-3-cache-token-manager.md) |
| Task 4: 实现单飞刷新、回退与压力测试 | 单飞刷新、并发与压测 | [task-4-single-flight-fallback.md](task-4-single-flight-fallback.md) |
| Task 5: 增加 CLI 双入口与脱敏诊断输出 | CLI 子命令与脱敏输出 | [task-5-cli-diagnosis.md](task-5-cli-diagnosis.md) |
| Task 6: 补齐学习笔记、CI 验证与测试报告 | 文档、CI、变更日志与测试报告 | [task-6-docs-ci-report.md](task-6-docs-ci-report.md) |
| 指标对比 | 改造前后指标对照 | [metrics-comparison.md](metrics-comparison.md) |
| Plan Self-Review | 计划自查：Spec 覆盖、占位扫描、类型一致性 | [plan-self-review.md](plan-self-review.md) |
