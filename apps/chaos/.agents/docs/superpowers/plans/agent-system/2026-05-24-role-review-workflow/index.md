# Role Review Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-24-role-review-workflow.md，已原子化拆分

**Goal:** 为 AgentForge 引入首条多角色协作工作流，用 Organization Steward → Execution Orchestrator → Collaboration Architect → Governance Auditor 的顺序门禁审批新增角色，并产出 4 份真实试运行审查记录。

**Architecture:** `.agents/workflows/role-review.md` 作为工作流主文档，`.agents/workflows/role-review/templates/` 承载提案模板，`.agents/workflows/role-review/verification/` 承载试运行审查记录。同时更新 `.agents/roles/README.md` 角色清单和协作元模型参考页的目录映射。

**Tech Stack:** Markdown、Mermaid、Git。

## 概述

本计划为 AgentForge 引入首条多角色协作工作流，通过四道顺序门禁（Organization Steward → Execution Orchestrator → Collaboration Architect → Governance Auditor）审批新增角色，并产出 4 份真实试运行审查记录。计划包含 5 个任务：创建工作流主文档与提案模板、生成 4 份试运行审查记录、更新角色清单、更新协作元模型目录映射、验收校验。

## 原子单元索引

| 序号 | 文件 | 主题 |
|---|---|---|
| 1 | [task-1-workflow-and-template.md](task-1-workflow-and-template.md) | Task 1: 创建工作流主文档与提案模板 |
| 2 | [task-2-gate-records.md](task-2-gate-records.md) | Task 2: 生成 4 份试运行审查记录 |
| 3 | [task-3-roles-readme.md](task-3-roles-readme.md) | Task 3: 更新 roles/README.md 角色清单 |
| 4 | [task-4-metamodel-mapping.md](task-4-metamodel-mapping.md) | Task 4: 更新协作元模型参考页目录映射 |
| 5 | [task-5-verification.md](task-5-verification.md) | Task 5: 验收校验 |
