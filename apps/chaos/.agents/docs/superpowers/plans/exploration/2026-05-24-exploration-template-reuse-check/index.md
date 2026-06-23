# Exploration Template Reuse Check Implementation Plan

> **别名**：曾用名 2026-05-24-exploration-template-reuse-check.md，已原子化拆分

## 元数据

- **原标题**: Exploration Template Reuse Check Implementation Plan
- **拆分日期**: 2026-06-23
- **原始行数**: 231
- **原子单元数**: 2

## 概述

本计划验证更新后的探索工作台模板是否能支撑新一轮探索，并确认 `Expected Evidence` 是否降低闭环证据收尾摩擦。

本计划继续采用文档驱动、只读验证优先的探索方式。第三轮工作台已位于 `.trae/specs/exploration-template-reuse-check/`，执行时只补充临时验证记录、复盘文件，并在 checklist/tasks 中反映完成状态。本轮不新增脚本，不修改产品代码。

**Tech Stack:** Markdown, Git, PowerShell, `uv run pytest`, `uv run pre-commit run --all-files`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## 原子单元索引

| 顺序 | 文件 | 主题 | 对应原章节 |
|------|------|------|-----------|
| 1 | [check-record.md](./check-record.md) | 检查记录：确认工作台基线并创建手动验证记录 | Task 1: Confirm Workbench Baseline + Task 2: Create Manual Validation Record |
| 2 | [retrospective.md](./retrospective.md) | 复盘记录：撰写复盘、收尾工作台并完成验证审查 | Task 3: Write Retrospective and Close Workbench + Task 4: Validate and Review + Self-Review |
