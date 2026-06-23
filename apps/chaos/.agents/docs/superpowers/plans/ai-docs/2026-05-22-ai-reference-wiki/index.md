# AI Reference Wiki Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 `2026-05-22-ai-reference-wiki.md`，已原子化拆分

## 概述

**Goal:** 在 `.agents/docs/` 下创建一套面向 AI 的参考 wiki 骨架，覆盖 `references`、`issue-patterns`、`integrations`、`sources` 和 `templates` 五类文档资产。

**Architecture:** 保持现有 `docs/` 与 `.agents/docs/` 的边界不变，只在 `.agents/docs/` 下新增参考知识区。通过分层目录、各级 `README.md`、种子页和统一模板，形成"导航页 + 主题页 + 来源页"的稳定结构，方便 agent 快速检索与后续持续补充内容。

**Tech Stack:** Markdown, AgentForge `.agents/` conventions, VS Code diagnostics

## 原子单元索引

| 序号 | 原子单元文件 | 主题 | 原文章节 |
| --- | --- | --- | --- |
| 1 | [task-1-top-level-directories.md](./task-1-top-level-directories.md) | 创建顶级 Wiki 目录骨架与索引页 | Task 1: Create Top-Level Wiki Directories And Index Pages |
| 2 | [task-2-python-podman-references.md](./task-2-python-podman-references.md) | 添加 Python 与 Podman 参考入口点 | Task 2: Add Python And Podman Reference Entry Points |
| 3 | [task-3-issue-patterns-integrations.md](./task-3-issue-patterns-integrations.md) | 添加问题模式与项目集成页 | Task 3: Add Issue Patterns And Project Integration Pages |
| 4 | [task-4-raw-sources-validation.md](./task-4-raw-sources-validation.md) | 添加原始来源入口并验证结构 | Task 4: Add Raw Source Topic Entrypoints And Validate The Structure |
| 5 | [task-5-optional-seed-pages.md](./task-5-optional-seed-pages.md) | 可选的后续种子页 | Task 5: Optional Follow-Up Seed Pages |

## 拆分说明

本文件由原 `2026-05-22-ai-reference-wiki.md`（667 行）原子化拆分而来，按 Task 边界切分为 5 个独立单元。每个原子单元保留原章节的完整内容（包括 Files 清单、Step 步骤、代码块与提交指令），可独立阅读与执行。
