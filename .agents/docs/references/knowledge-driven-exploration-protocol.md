# Knowledge-Driven Exploration Protocol

## Search Keywords

- 主关键词：探索协议、知识驱动探索、探索闭环、知识回流、探索型能力底座
- 英文术语：knowledge-driven exploration, exploration protocol, exploration loop, knowledge feedback loop
- 常见别名：探索底座协议、探索主线协议、知识沉淀协议
- 错误短语：无

## Goal

定义 AgentForge 中一次探索动作从立项到回流的统一协议，确保比赛、应用与技能生态三类探索都能复用同一条知识主线。

## Relevance In AgentForge

- 关联模块：`.agents/docs/templates/`、`.agents/docs/superpowers/specs/`、`.agents/docs/superpowers/retrospectives/`、`.trae/specs/`
- 常见触发场景：规划新的探索方向、设计最小试点、沉淀执行模板、复盘并升级规则
- 优先检查文件：`.agents/docs/superpowers/specs/2026-05-24-knowledge-driven-exploration-foundation-design.md`

## Trigger Phrases

- 如何把一个探索想法变成可执行闭环
- 比赛、应用和技能生态怎么共用一套探索流程
- 探索结束后经验应该沉淀到哪里
- 怎样定义探索完成而不只是“做过了”

## Core Flow

```mermaid
flowchart LR
    A["探索想法"] --> B["场景卡"]
    B --> C["Spec"]
    C --> D["Plan"]
    D --> E["验证"]
    E --> F["复盘"]
    F --> G["回流更新"]
    G --> B
```

## Required Inputs

- `探索动机`：为什么现在要做这次探索
- `场景描述`：这次探索对应的真实问题空间
- `目标约束`：时间盒、边界、资源或风险约束
- `成功标准`：什么结果可以判定探索成立
- `已有参考`：现有文档、模板、历史试点或相关仓库资产

## Required Outputs

- `场景卡`：把探索问题表达为统一字段
- `设计 spec`：把场景卡展开为正式设计边界
- `执行计划`：把 spec 拆成可执行任务
- `验证记录`：记录演示、检查或阶段验收结果
- `复盘文档`：把经验回流到模板、规则或场景目录

## Gate Rules

- 没有场景卡，不进入 spec
- 没有 spec，不进入正式计划
- 没有验证，不判定探索完成
- 没有复盘回流，不算底座能力增长

## Layer Mapping

- `共性知识层`：统一资产与字段，是单一事实来源
- `场景适配层`：比赛、应用、技能生态三类轻量适配视图
- `轻工作流层`：推进探索动作，但不承担长期知识归档
- `回流演化层`：把偏差和经验反馈为模板、规则或目录更新

## Initial Deliverables

1. `统一探索协议页`
2. `三类探索场景卡视图`
3. `探索 spec 母模板`
4. `最小执行工作台模板`
5. `复盘回流模板`

## Recommended Pilot

- 试点主题：`探索任务知识闭环最小试点`
- 推荐原因：它能最低成本验证 `场景卡 -> spec -> plan -> 验证 -> 复盘 -> 回流` 是否真的成立

## Related Files

- [`../templates/dao-scenario-card-template.md`](../templates/dao-scenario-card-template.md)
- [`../templates/knowledge-driven-exploration-spec-template.md`](../templates/knowledge-driven-exploration-spec-template.md)
- [`../templates/knowledge-driven-exploration-retrospective-template.md`](../templates/knowledge-driven-exploration-retrospective-template.md)
- [`../../../../.trae/specs/exploration-knowledge-loop-pilot/spec.md`](../../../../.trae/specs/exploration-knowledge-loop-pilot/spec.md)

## Sources

- 设计来源：`.agents/docs/superpowers/specs/2026-05-24-knowledge-driven-exploration-foundation-design.md`
- 版本：2026-05-24
- 抓取时间：不适用
