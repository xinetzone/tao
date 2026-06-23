# 采纳与收尾（Adoption and Closure）

> 本单元涵盖原文件的 First-Phase Adoption Plan、Planned Touchpoints、Explicit Non-Goals for Phase 1、Acceptance Criteria、Risks、Open Questions Deferred 章节，给出首版落地顺序、影响入口、验收标准与风险。

## First-Phase Adoption Plan

推荐采用最小落地顺序：

1. 先定义元模型：形成正式参考 spec，固化实体、关系、边界和状态语义。
2. 再定义治理映射：明确现有入口文件和目录分别位于哪一层、对应哪些实体。
3. 最后收敛入口：只在少量关键入口文件补充协作语义导航，不大规模调整目录结构。
4. 作为第一批试点目录引入 `.agents/roles/`，用于验证语义实例承载方式。
5. 在 `roles/` 稳定后，再受控评估 `.agents/teams/`、`.agents/agents/`、`.agents/policies/`。

## Planned Touchpoints

第一版建议影响以下入口：

- `AGENTS.md`
- `.agents/README.md`
- `.agents/docs/references/`
- `.agents/roles/`（首批试点）

说明：

- `AGENTS.md` 适合补充协作语义入口和治理总览
- `.agents/README.md` 适合补充目录与元模型的语义映射
- `.agents/docs/references/` 适合作为后续稳定参考页的长期承载位置
- `.agents/roles/` 作为第一批试点目录，用于承载职责模板、权限边界与默认规则绑定

## Explicit Non-Goals for Phase 1

第一版明确不做：

- 多智能体运行时调度器
- 配置驱动实例化规范
- 权限引擎和审批流实现
- 跨 team 状态同步机制
- 对现有规则体系的大规模重写
- 一次性引入完整的 `teams/`、`agents/`、`policies/` 目录矩阵

## Acceptance Criteria

- 存在一份可独立阅读的协作元模型设计稿
- 设计稿明确区分 `MetaModel Layer` 与 `Governance Layer`
- 设计稿明确 5 个领域与 15 个核心实体
- 设计稿明确关键关系、强约束、弱约束和最小状态语义
- 设计稿明确当前项目主要目录在协作模型中的映射位置
- 设计稿明确第一版做什么、不做什么，以及推荐落地顺序

## Risks

- 如果后续直接进入运行时实现而不先补治理映射，元模型会重新退化为术语表
- 如果把 `Role`、`Permission`、`Rule` 混用，治理层会快速失去边界
- 如果把 `Workflow` 设计成知识容器，会造成执行层与知识层耦合
- 如果在第一版就绑定具体配置格式，可能削弱跨项目迁移能力

## Open Questions Deferred

以下问题被明确延后到后续阶段：

- 配置层的实例化语法采用什么格式
- 运行时协作是否采用事件驱动或状态机实现
- 跨 team 的权限继承与冲突解析如何落地
- `Artifact` 与长期知识回流之间的自动化机制如何实现
- `Session` 是否需要拆分为事件、快照和恢复三个对象
