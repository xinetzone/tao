# Dao Business Mapping Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **别名**：曾用名 2026-05-23-dao-business-mapping-framework.md，已原子化拆分

**Goal:** 将《道德经》哲学到业务落地的全链路框架，从设计稿转化为仓库中的稳定参考资产、可复用模板、示例场景库与导航入口。

**Architecture:** 实施分为四个独立但串联的文档单元。先把设计稿提炼为稳定参考页，再补充可复用模板与示例场景库，最后把这些资产接入现有导航与哲学总纲，形成“参考解释 -> 场景执行 -> 导航检索”的闭环。整个过程只修改 `.agents/docs/` 范围内的 AI 文档资产，不触碰人类文档树。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, VS Code diagnostics, Git

---

## 概述

本计划将《道德经》哲学到业务落地的全链路框架从设计稿转化为仓库中的稳定参考资产、可复用模板、示例场景库与导航入口。整个实施分为五个独立但串联的任务单元，形成“参考解释 -> 场景执行 -> 导航检索 -> 最终验证”的闭环。所有改动仅限 `.agents/docs/` 范围内的 AI 文档资产，不触碰人类文档树。

## File Structure

- Create: `.agents/docs/references/dao-business-mapping-framework.md`
  - 作用：沉淀稳定版的全链路框架说明，作为后续 AI 与人类共同引用的主入口。
- Create: `.agents/docs/templates/dao-scenario-card-template.md`
  - 作用：提供标准场景卡模板，供后续 spec、plan、retrospective 复用。
- Create: `.agents/docs/references/dao-scenario-catalog.md`
  - 作用：存放首批 3 个示例场景，证明框架可跨层复用。
- Modify: `.agents/docs/README.md`
  - 作用：接入新框架与场景库入口。
- Modify: `.agents/docs/references/README.md`
  - 作用：将新参考页和场景库加入 `references/` 导航。
- Modify: `.agents/docs/references/dao-tech-foundation.md`
  - 作用：将哲学总纲与执行层框架互相链接，避免两份文档割裂。

## 原子单元索引

| 序号 | 文件 | 主题 | 说明 |
|---|---|---|---|
| 1 | [task-1-framework-reference.md](./task-1-framework-reference.md) | 框架参考页 | 创建稳定版的全链路框架说明参考页 |
| 2 | [task-2-scenario-card-template.md](./task-2-scenario-card-template.md) | 场景卡模板 | 添加可复用的场景卡模板 |
| 3 | [task-3-scenario-catalog.md](./task-3-scenario-catalog.md) | 场景目录 | 创建首批示例场景库 |
| 4 | [task-4-navigation-update.md](./task-4-navigation-update.md) | 导航更新 | 将框架接入现有导航 |
| 5 | [task-5-final-verification.md](./task-5-final-verification.md) | 最终验证与移交 | 最终验证与移交总结 |
