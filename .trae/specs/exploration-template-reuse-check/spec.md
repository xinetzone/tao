# Spec

## Goal

- 验证更新后的探索工作台模板是否能直接支撑新一轮探索，并确认 `Expected Evidence` 是否降低收尾时查找闭环证据的摩擦。

## Scope

- 使用当前工作台模板创建 `exploration-template-reuse-check` 探索工作台。
- 明确本轮模板复用检查的目标、边界、交付物与风险。
- 执行一次只读最小验证，检查本轮工作台能否在收尾时集中指向协议、场景、工作台、复盘与回流动作。
- 输出复盘并给出至少一个 `Next Action`。

## Non-Goals

- 本轮不新增自动化脚本。
- 本轮不重构 `.agents/docs` 信息架构。
- 本轮不大规模修改探索协议页。
- 本轮不处理业务功能或产品代码。

## Deliverables

- `.trae/specs/exploration-template-reuse-check/spec.md`
- `.trae/specs/exploration-template-reuse-check/tasks.md`
- `.trae/specs/exploration-template-reuse-check/checklist.md`
- `.temp/exploration-template-reuse-check.md`
- `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-template-reuse-check.md`

## Risks

- 如果只用本轮自身作为样本，结论可能偏向模板自证，无法覆盖复杂真实探索。
- 如果证据链仍然分散，可能需要继续强化协议页或复盘模板，而不是立即脚本化。
- 如果没有出现 `WARN` 或 `MISSING`，仍不能证明未来不需要自动化，只能说明当前样本可手工处理。
