# CLI Status Diagnostics Exploration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-24-cli-status-diagnostics-exploration.md，已原子化拆分

**Goal:** 验证 AgentForge 当前 CLI 状态/诊断体验是否能支撑用户定位 GitHub App 配置、策略、缓存与错误路径问题，并沉淀后续开发动作。

**Architecture:** 本计划采用文档驱动、只读验证优先的探索方式。工作台位于 `.trae/specs/cli-status-diagnostics-exploration/`，执行时只补充 `.temp/` 临时验证记录、复盘文件，并更新工作台 checklist/tasks 的完成状态。本轮不修改产品代码，不访问外部服务，不处理真实凭据。

**Tech Stack:** Markdown, Python source reading, pytest test inventory, Git, PowerShell, `uv run pytest`, `uv run pre-commit run --all-files`

---

## 概述

本计划验证 AgentForge 当前 CLI 状态/诊断体验是否能支撑用户定位 GitHub App 配置、策略、缓存与错误路径问题，并沉淀后续开发动作。计划采用文档驱动、只读验证优先的探索方式，分为两个独立阶段：探索验证记录（确认 CLI 诊断基线、创建手动验证记录、运行测试与预提交校验）与复盘记录（输出真实开发议题探索复盘并关闭工作台）。整个过程不修改产品代码，不访问外部服务，不处理真实凭据。

## 原子单元索引

| 单元名 | 主题 | 链接 |
|--------|------|------|
| Exploration Check | 探索验证记录：确认 CLI 诊断基线、创建手动验证记录、运行测试与预提交校验 | [exploration-check.md](./exploration-check.md) |
| Retrospective | 复盘记录：输出真实开发议题探索复盘并关闭工作台 | [retrospective.md](./retrospective.md) |
