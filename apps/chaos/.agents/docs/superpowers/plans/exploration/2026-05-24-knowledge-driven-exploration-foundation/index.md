# Knowledge-Driven Exploration Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-24-knowledge-driven-exploration-foundation.md，已原子化拆分

**Goal:** 将"知识沉淀驱动的探索型能力底座"从设计稿落实为可复用协议页、模板资产、最小工作台样例与导航入口，并用一个真实试点打通闭环。

**Architecture:** 实施分为六个串联文档单元。先把设计稿固化为稳定协议页，再升级场景卡与新增 spec / 复盘 / 工作台模板，随后创建首个 `.trae` 试点实例并把它回填到场景目录与导航中，最后做整体验证。整个过程只修改 `.agents/docs/` 与 `.trae/` 下的文档资产，不触碰业务代码。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, `.trae` workspace structure, VS Code diagnostics, Git

---

## 概述

本计划将"知识沉淀驱动的探索型能力底座"从设计稿落实为可复用协议页、模板资产、最小工作台样例与导航入口，并用一个真实试点打通闭环。实施分为六个串联文档单元，覆盖协议页创建、场景卡模板升级、spec/复盘模板、工作台模板与试点、场景目录注册、导航接入与最终验证。整个过程只修改 `.agents/docs/` 与 `.trae/` 下的文档资产，不触碰业务代码。

## File Structure

- Create: `.agents/docs/references/knowledge-driven-exploration-protocol.md`
  - 作用：作为探索型能力底座的稳定协议页，沉淀统一输入、输出、门禁规则与试点建议。
- Modify: `.agents/docs/templates/dao-scenario-card-template.md`
  - 作用：在现有场景卡模板上增加比赛型、应用型、技能生态型三种轻量视图，避免创建平行模板。
- Create: `.agents/docs/templates/knowledge-driven-exploration-spec-template.md`
  - 作用：提供探索 spec 母模板，约束目标、非目标、能力闭环与回流计划。
- Create: `.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md`
  - 作用：提供复盘模板，强制回答复用、脆弱点、升级建议与适用范围。
- Create: `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md`
  - 作用：定义 `.trae/specs/<topic>/` 工作台的最小文件结构与字段。
- Create: `.trae/specs/exploration-knowledge-loop-pilot/spec.md`
  - 作用：承载首个"探索任务知识闭环最小试点"的执行中 spec。
- Create: `.trae/specs/exploration-knowledge-loop-pilot/tasks.md`
  - 作用：承载首个试点的执行任务列表与依赖关系。
- Create: `.trae/specs/exploration-knowledge-loop-pilot/checklist.md`
  - 作用：承载首个试点的验收清单。
- Modify: `.agents/docs/references/dao-scenario-catalog.md`
  - 作用：将"探索任务知识闭环最小试点"加入长期场景目录，建立设计与试点之间的回流关系。
- Modify: `.agents/docs/README.md`
  - 作用：把探索协议页接入 AI 文档导航。
- Modify: `.agents/docs/references/README.md`
  - 作用：把探索协议页加入 `references/` 当前入口列表。

## 原子单元索引

| 单元名 | 主题 | 链接 |
|--------|------|------|
| Task 1: Protocol Page | 创建稳定的探索协议页 | [task-1-protocol-page.md](./task-1-protocol-page.md) |
| Task 2: Scenario Card Template | 升级共享场景卡模板 | [task-2-scenario-card-template.md](./task-2-scenario-card-template.md) |
| Task 3: Spec And Retrospective Templates | 创建 spec 与复盘模板 | [task-3-spec-and-retrospective-templates.md](./task-3-spec-and-retrospective-templates.md) |
| Task 4: Workbench Template And Pilot Workspace | 创建工作台模板与首个试点工作台 | [task-4-workbench-template-and-pilot-workspace.md](./task-4-workbench-template-and-pilot-workspace.md) |
| Task 5: Pilot Scenario Catalog Registration | 在长期场景目录中注册试点 | [task-5-pilot-scenario-catalog-registration.md](./task-5-pilot-scenario-catalog-registration.md) |
| Task 6: Navigation And Final Verification | 接入导航并运行最终验证 | [task-6-navigation-and-final-verification.md](./task-6-navigation-and-final-verification.md) |
