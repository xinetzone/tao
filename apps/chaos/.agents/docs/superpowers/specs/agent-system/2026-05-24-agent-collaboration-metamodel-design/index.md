# Agent Collaboration Metamodel Design

> **别名**：曾用名 2026-05-24-agent-collaboration-metamodel-design.md，已原子化拆分

## 元数据

- **原标题**：Agent Collaboration Metamodel Design
- **原文件**：`2026-05-24-agent-collaboration-metamodel-design.md`（477 行）
- **拆分日期**：2026-05-24
- **原子单元数**：5
- **拆分位置**：`agent-system/2026-05-24-agent-collaboration-metamodel-design/`

## 概述

本设计稿为 `AgentForge` 增加一套面向多 team、多角色、多智能体协作的统一语义内核，用于在不提前绑定配置格式、运行时引擎或具体平台实现的前提下，先定义稳定、可迁移、可复用的协作元模型。

设计采用 `MetaModel Layer + Governance Layer` 的双层结构，覆盖组织、任务、知识三类关系，并补齐治理与运行态语义边界。首版收敛为 5 个领域与 15 个核心实体，并将当前 `AGENTS.md`、`.agents/`、`.trae/` 等既有结构映射到协作元模型中，为后续配置驱动、运行时编排、权限治理和审计能力预留清晰边界。

## 原子单元索引

| 序号 | 文件 | 主题 | 涵盖原章节 |
|---|---|---|---|
| 1 | [part-1-overview-and-decision.md](part-1-overview-and-decision.md) | 概述与决策 | Goal、Background、Scope、Non-Goals、Design Principles、Options Considered、Recommendation |
| 2 | [part-2-metamodel-layer.md](part-2-metamodel-layer.md) | 元模型层 | Architecture Layers、Domains、Core Entities、Relationship Model |
| 3 | [part-3-governance-layer.md](part-3-governance-layer.md) | 治理层 | Constraints、State Semantics |
| 4 | [part-4-directory-mapping.md](part-4-directory-mapping.md) | 目录映射 | Directory Mapping、Semantic Directories Evolution |
| 5 | [part-5-adoption-and-closure.md](part-5-adoption-and-closure.md) | 采纳与收尾 | First-Phase Adoption Plan、Planned Touchpoints、Explicit Non-Goals for Phase 1、Acceptance Criteria、Risks、Open Questions Deferred |

## 阅读建议

- 首次阅读建议按 1→5 顺序通读，以获得完整设计脉络。
- 各原子单元均可独立阅读：单元 1 提供目标与决策背景；单元 2-3 构成双层语义内核；单元 4 解释现有目录映射；单元 5 给出落地顺序与验收标准。
- 所有原始内容已完整保留，未做删改或重写。
