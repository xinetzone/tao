# Agent Collaboration Metamodel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-24-agent-collaboration-metamodel.md，已原子化拆分

**Goal:** 为 AgentForge 落地第一阶段协作元模型入口，补齐稳定参考页、入口导航，并将 `.agents/roles/` 作为首个语义实例目录试点引入。

**Architecture:** 本阶段只实现“语义层 + 导航层 + 最小实例层”三部分。`.agents/docs/references/` 承载稳定参考页，`AGENTS.md` 与 `.agents/README.md` 负责全局路由和目录映射，`.agents/roles/` 作为 `Role` 的首个实例承载目录验证目录化方向，不引入运行时编排或配置引擎。

**Tech Stack:** Markdown、Mermaid、Git、项目既有 `.agents/` 文档体系。

---

## 概述

本计划为 AgentForge 落地第一阶段协作元模型入口，拆分为 4 个原子任务单元：收敛 Spec 与稳定参考页、更新全局入口与目录导航、引入 roles 首批试点目录、回填引用与验收校验。每个原子单元专注单一主题，可独立阅读与执行。

## 原子单元索引

| 序号 | 文件 | 主题 | 说明 |
|---|---|---|---|
| 1 | [task-1-reference-page.md](./task-1-reference-page.md) | 收敛 Spec 与稳定参考页 | 将 spec 中目录演进表述收敛为 roles 首批试点，生成稳定参考页骨架并补齐为可独立阅读版本 |
| 2 | [task-2-global-entry-navigation.md](./task-2-global-entry-navigation.md) | 更新全局入口与目录导航 | 为 AGENTS.md 与 .agents/README.md 增加协作元模型导航与目录语义映射 |
| 3 | [task-3-roles-pilot-directory.md](./task-3-roles-pilot-directory.md) | 引入 .agents/roles/ 首批试点目录 | 创建 roles 目录说明页与首个试点角色文件 collaboration-architect |
| 4 | [task-4-backfill-and-acceptance.md](./task-4-backfill-and-acceptance.md) | 回填引用与验收校验 | 检查占位词、相对路径、Mermaid 语法与改动范围，完成最终提交 |
