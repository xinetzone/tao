# 探索任务知识闭环最小试点

## Goal

以最小成本验证探索型能力底座能否稳定串起"场景卡 → spec → plan → 验证 → 复盘 → 回流"完整链路，证明知识底座可以先于复杂工作流成立。

## Background

### 当前上下文

- 项目已具备较完整的知识资产目录结构（`.agents/docs/` 与 `.trae/`）
- 已产出 4 个场景卡示例（见 `.agents/docs/references/dao-scenario-catalog.md`）
- 已完成统一探索协议页、spec 母模板、工作台模板与复盘模板
- 本次试点是探索型能力底座设计的首个正式验证

### 已有相关资产

- `.agents/docs/references/knowledge-driven-exploration-protocol.md`：统一探索协议
- `.agents/docs/templates/dao-scenario-card-template.md`：场景卡模板
- `.agents/docs/templates/knowledge-driven-exploration-spec-template.md`：spec 母模板
- `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md`：工作台模板
- `.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md`：复盘模板
- `.agents/docs/superpowers/specs/2026-05-24-knowledge-driven-exploration-foundation-design.md`：底座设计稿

### 为什么现在做

- 底座设计稿已通过评审，首批产物（协议页 + 4 个模板）已落位
- 需要一次真实试点来验证链路是否低摩擦、可复用、可回流、可扩展
- 如果底座先在"自我验证"这个最小闭环上跑通，后续切换到比赛型或应用型只需更换场景

## Scope

- 在 `.trae/specs/exploration-knowledge-loop-pilot/` 下创建并维护完整工作台（spec、tasks、checklist）
- 按协议执行：场景卡校验 → spec → plan → 最小验证 → 复盘
- 产出至少一条可执行的回流动作（更新模板、规则、协议或场景目录）
- 记录摩擦点与复用情况，作为后续迭代输入

## Non-Goals

- 本次不实现自动化工作流或脚本
- 本次不为比赛型或应用型探索做预设计
- 本次不新增模板字段（如有需求，记录到复盘建议）
- 本次不扩展协议层以外的新目录结构

## Core Loop

```mermaid
flowchart LR
    A["场景卡校验"] --> B["Spec 展开"]
    B --> C["Plan 拆解"]
    C --> D["最小验证"]
    D --> E["复盘"]
    E --> F["回流动作"]
    F --> A
```

- 场景卡已存在于 `dao-scenario-catalog.md`，本次从校验其字段完整性开始
- spec（本文档）将场景卡展开为正式设计边界
- plan 将 spec 拆为可执行任务，输出到 `tasks.md`
- 最小验证：完成 checklist 全部勾选，确认证据链完整
- 复盘输出到 `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-knowledge-loop-pilot.md`
- 回流动作至少包含一项对底座资产的实质性更新

## Layer Mapping

- 共性知识层：协议页、场景卡模板、spec 母模板、工作台模板、复盘模板
- 场景适配层：本次为技能生态型探索，适配字段聚焦触发条件、输入输出契约与评测口径
- 轻工作流层：`.trae/specs/exploration-knowledge-loop-pilot/` 下的 spec / tasks / checklist 三文件结构
- 回流演化层：复盘结束后，将经验反向写入模板、协议或场景目录

## Deliverables

1. 试点工作台三文件（spec.md、tasks.md、checklist.md）
2. 试点复盘文档（`.agents/docs/superpowers/retrospectives/2026-05-24-exploration-knowledge-loop-pilot.md`）
3. 至少一条回流动作（具体目标在复盘阶段确定）
4. 更新后的 `dao-scenario-catalog.md`（试点状态从"试点"更新为"已完成"）

## Validation

- 低摩擦：从场景卡到 spec 是否自然进入，不增加明显流程负担
- 可复用：本次产出的模板与工作台结构能否直接为下一个探索所用
- 可回流：复盘能否实质更新模板、规则或场景目录
- 可扩展：后续接入比赛型或应用型时，是否只需要薄适配

## Risks

- 如果试点停留在"写完 spec 和 tasks"而没有进入验证与复盘，会误判底座已经成立
- 如果在执行中被其他任务打断，探索上下文会丢失（工作台三文件结构本身正是对此的防御）
- 如果回流动作仅是"更新文件"而没有改变后续探索的行为，底座退化风险高

## Rollback Or Adjustment

- 如果试点跑不通，优先检查：场景卡字段是否完整、spec 边界是否过宽、plan 是否可执行
- 如果模板本身是摩擦来源，复盘时应记录为升级建议，不在此轮试点中直接修改模板
- 如果时间盒压力大，允许缩减验证范围，但复盘与回流不可跳过

## Next Step

- 进入 plan 的条件：本文档（spec）已确认边界清晰，场景卡字段已校验完整
- 进入方式：在 `tasks.md` 中拆解执行任务，并按 `checklist.md` 逐项追踪
