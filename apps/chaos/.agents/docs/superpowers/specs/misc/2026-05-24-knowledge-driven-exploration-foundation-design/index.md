---
title: Knowledge-Driven Exploration Foundation Design
date: 2026-05-24
type: spec
status: atomized
original_file: 2026-05-24-knowledge-driven-exploration-foundation-design.md
---

# Knowledge-Driven Exploration Foundation Design

> **别名**：曾用名 2026-05-24-knowledge-driven-exploration-foundation-design.md，已原子化拆分

## 概述

本设计稿为 `AgentForge` 建立一套以知识沉淀为核心的探索型能力底座，用于统一承载比赛型探索、应用型探索与技能生态型探索，避免每次从零组织思路、重复发明流程或让经验停留在对话里。

设计采用双层底座型方案（Option C），将探索型能力底座分为 4 层：共性知识层、场景适配层、轻工作流层、回流演化层。统一探索协议定义为"任何探索动作，都必须从结构化输入进入，并产出可回流的结构化结果"，并固定流转路径为 `场景卡 -> spec -> plan -> 验证 -> 复盘 -> 回流`。

本文件为原子化拆分后的索引页，原始 16 个章节已按主题拆分为 13 个独立原子单元，完整保留全部原始内容。

## 原子单元索引

| 序号 | 文件 | 主题 | 原始章节 |
|---|---|---|---|
| 1 | [part-01-goal-and-background.md](part-01-goal-and-background.md) | 目标与背景 | Goal, Background |
| 2 | [part-02-scope-and-non-goals.md](part-02-scope-and-non-goals.md) | 范围与边界 | Scope, Non-Goals |
| 3 | [part-03-design-principles.md](part-03-design-principles.md) | 设计原则 | Design Principles |
| 4 | [part-04-options-and-recommendation.md](part-04-options-and-recommendation.md) | 方案选型与决策 | Options Considered, Recommendation |
| 5 | [part-05-architecture-layers.md](part-05-architecture-layers.md) | 架构分层 | Architecture Layers |
| 6 | [part-06-protocol.md](part-06-protocol.md) | 探索协议 | Protocol |
| 7 | [part-07-directory-mapping.md](part-07-directory-mapping.md) | 目录映射 | Directory Mapping |
| 8 | [part-08-initial-deliverables.md](part-08-initial-deliverables.md) | 首批交付物 | Initial Deliverables |
| 9 | [part-09-initial-build-order.md](part-09-initial-build-order.md) | 建设顺序 | Initial Build Order |
| 10 | [part-10-pilot-strategy.md](part-10-pilot-strategy.md) | 试点策略 | Pilot Strategy |
| 11 | [part-11-validation-model.md](part-11-validation-model.md) | 验证模型 | Validation Model |
| 12 | [part-12-risks.md](part-12-risks.md) | 风险 | Risks |
| 13 | [part-13-acceptance-criteria.md](part-13-acceptance-criteria.md) | 验收标准 | Acceptance Criteria |
