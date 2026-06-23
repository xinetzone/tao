# Exploration Reference Integrity Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-24-exploration-reference-integrity-check.md，已原子化拆分

**Goal:** 验证探索闭环中的关键引用关系是否能用低成本、只读方式被检查，并用上一轮试点完成一次手工验证。

**Architecture:** 本计划不引入脚本或自动修复逻辑，而是先把只读检查规则落为结构化文档，再用 `exploration-knowledge-loop-pilot` 作为样本执行一次手工检查。检查结果进入 `.temp/` 作为临时验证记录，最终复盘归档到 `.agents/docs/superpowers/retrospectives/` 并产生至少一个回流动作。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, `.trae` workspace structure, PowerShell, uv, pytest, pre-commit

---

## 概述

本计划验证探索闭环中的关键引用关系是否能用低成本、只读方式被检查，并用上一轮试点完成一次手工验证。实施不引入脚本或自动修复逻辑，而是先把只读检查规则落为结构化文档，再用 `exploration-knowledge-loop-pilot` 作为样本执行一次手工检查。检查结果进入 `.temp/` 作为临时验证记录，最终复盘归档到 `.agents/docs/superpowers/retrospectives/` 并产生至少一个回流动作。整个计划分为两个独立阶段：检查记录阶段（确认检查集合并执行手工验证）与复盘记录阶段（归档复盘、标记工作台完成并验证产出）。

## File Structure

- Read: `.trae/specs/exploration-reference-integrity-check/spec.md`
  - 作用：第二轮探索的设计边界与最小检查集合。
- Modify: `.trae/specs/exploration-reference-integrity-check/tasks.md`
  - 作用：记录本轮探索执行状态。
- Modify: `.trae/specs/exploration-reference-integrity-check/checklist.md`
  - 作用：记录本轮探索验收状态。
- Create: `.temp/exploration-reference-integrity-check.md`
  - 作用：临时手工检查记录；用于验证，不进入长期知识库。
- Create: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md`
  - 作用：本轮探索复盘与回流动作归档。
- Read: `.agents/docs/references/knowledge-driven-exploration-protocol.md`
  - 作用：确认协议页引用模板与试点工作台。
- Read: `.agents/docs/references/dao-scenario-catalog.md`
  - 作用：确认长期场景目录包含上一轮试点场景。
- Read: `.agents/docs/README.md`
  - 作用：确认 AI 文档导航包含探索协议或场景目录入口。
- Read: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-knowledge-loop-pilot.md`
  - 作用：确认上一轮复盘位置与 Next Action。

## 原子单元索引

| 单元名 | 主题 | 链接 |
|--------|------|------|
| Check Record | 确认最小只读检查集合并使用试点样本执行手工验证 | [check-record.md](./check-record.md) |
| Retrospective | 归档第二轮复盘、标记工作台完成并验证探索产出 | [retrospective.md](./retrospective.md) |
