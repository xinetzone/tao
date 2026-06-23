# Agent Memory Dream Protocol Implementation Plan

> **别名**：曾用名 2026-05-24-agent-memory-dream-protocol.md，已原子化拆分

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## 概述

本计划目标是将已确认的“记忆、做梦”知识协议从独立文档资产推进为可发现、可试用、可验证、可回流的 AgentForge 认知协议。

实施分为四个串联文档单元：先确认协议四件套已经存在并与设计一致，再把参考协议页接入 AI 文档导航，然后创建一个最小 `.trae` 试点工作台，最后用试点结果决定是否回流到规则、模板或参考页。整个过程只修改 `.agents/docs/` 与 `.trae/` 下的文档资产，不触碰 `src/taolib/` 运行时代码。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, `.trae` workspace structure, mise task runner, pre-commit

## 原子单元索引

| 文件 | 主题 |
|---|---|
| [overview.md](./overview.md) | 计划目标、架构与技术栈 |
| [file-structure.md](./file-structure.md) | 文件结构清单（Existing/Modify/Create/Future optional） |
| [task-1-verify-protocol-quartet.md](./task-1-verify-protocol-quartet.md) | Task 1：验证协议四件套已存在并符合设计 |
| [task-2-documentation-navigation.md](./task-2-documentation-navigation.md) | Task 2：把协议页接入 AI 文档导航 |
| [task-3-pilot-workbench.md](./task-3-pilot-workbench.md) | Task 3：创建最小 `.trae` 试点工作台（spec + tasks + checklist） |
| [task-4-validation-retrospective.md](./task-4-validation-retrospective.md) | Task 4：运行验证并决定是否产出复盘 |
| [self-review.md](./self-review.md) | 自审：Spec Coverage、Placeholder Scan、Consistency Check |
