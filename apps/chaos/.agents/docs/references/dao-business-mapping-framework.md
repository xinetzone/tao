# Dao Business Mapping Framework

## Search Keywords

- 主关键词：业务场景映射、哲学到技术、全链路框架、场景矩阵、验证清单
- 英文术语：business mapping framework, scenario matrix, validation checklist, philosophy-to-engineering
- 常见别名：道家业务框架、场景映射母版、业务转化框架
- 错误短语：无

## Goal

说明如何把《道德经》的哲学原则稳定转化为产品能力、技术模块、验证指标与业务场景，并为后续 spec、plan 与 retrospective 提供统一表达骨架。

## Relevance In AgentForge

- 关联模块：`AGENTS.md`、`.agents/docs/references/dao-tech-foundation.md`、`.agents/docs/templates/`、`.agents/docs/superpowers/`
- 常见触发场景：设计新方向、抽象业务能力、拆解技术方案、建立验证标准、沉淀复盘
- 优先检查文件：`AGENTS.md`、`.agents/docs/references/dao-tech-foundation.md`

## Trigger Phrases

- 如何把哲学原则转成业务能力
- 怎样用统一模板描述一个业务场景
- 这条方案如何验证是否符合大道至简
- 如何从哲学一路落到技术和复盘

## Core Chain

```mermaid
flowchart LR
    A["哲学原则"] --> B["产品能力"]
    B --> C["技术模块"]
    C --> D["验证指标"]
    D --> E["业务场景"]
    E --> F["复盘反馈"]
    F --> A
```

## Layer Definitions

- `哲学原则`：定义价值取向与设计判断准绳。
- `产品能力`：把哲学转成业务和用户可感知的能力单元。
- `技术模块`：把能力进一步落成模块、规则、工作流、技能或数据结构。
- `验证指标`：定义可观察的成功标准。
- `业务场景`：放入真实问题空间验证前四层是否成立。
- `复盘反馈`：将执行结果回流到抽象层，形成纠偏与再设计。

## Standard Mapping Unit

- `哲学命题`
- `工程解释`
- `对应能力`
- `技术落点`
- `验证方法`
- `适用场景`

## Validation Checklist

- 是否绑定了明确的哲学依据，而不是抽象口号
- 是否抽象出了独立、可感知的产品能力
- 是否映射到清晰的技术模块，而不是职责混杂
- 是否定义了可观察的验证指标
- 是否识别了风险与偏差路径
- 是否预留了复盘和纠偏入口

## Recommended Usage

1. 先阅读 `dao-tech-foundation.md` 理解哲学内核
2. 再使用本页的链路和检查项进行方案设计
3. 使用 `dao-scenario-card-template.md` 编写具体场景
4. 将代表性场景沉淀到 `dao-scenario-catalog.md`
5. 任务结束后在 `retrospectives/` 中复盘并回流

## Related Files

- [`dao-tech-foundation.md`](./dao-tech-foundation.md)
- [`dao-scenario-catalog.md`](./dao-scenario-catalog.md)
- [`../templates/dao-scenario-card-template.md`](../templates/dao-scenario-card-template.md)

## Sources

- 设计来源：`.agents/docs/superpowers/specs/2026-05-23-dao-business-mapping-framework-design.md`
- 版本：2026-05-23
- 抓取时间：不适用
