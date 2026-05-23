# Exploration Template Reuse Check Retrospective

## Outcome

- 本轮探索验证了更新后的探索工作台模板可以直接支撑新一轮探索启动。
- `Expected Evidence` 在计划阶段降低了闭环证据遗漏风险。
- 本轮发现复盘文件相关证据具有生命周期特征，在复盘创建前只能判定为 `WARN`，收尾后才能转为 `PASS`。

## Reused Foundation

- 复用了 `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md` 中新增的 `Expected Evidence` 小节。
- 复用了 `.trae/specs/exploration-template-reuse-check/` 作为第三轮探索工作台。
- 复用了上一轮引用完整性检查中的 `PASS`、`WARN`、`MISSING` 状态语义。

## Friction Points

- `Expected Evidence` 能提前暴露证据要求，但有些证据只有在收尾阶段才会存在。
- checklist 中的证据完整性检查适合作为收尾项，而不是启动项。
- 当前样本仍偏向机制自检，后续需要一次更贴近真实业务或研究议题的探索来验证模板泛化性。

## Validation Result

- 低摩擦：成立。新模板可以直接生成第三轮工作台。
- 可复用：成立。`Expected Evidence` 能被 checklist 直接承接。
- 可回流：成立。本轮发现可转化为模板使用说明或 checklist 解释。
- 可扩展：部分成立。仍需要真实议题样本验证。

## Upgrade Recommendations

- 保留 `Expected Evidence`，并把它视为收尾证据清单，而不是启动时必须全部满足的条件。
- 暂不新增自动化脚本，因为本轮 `WARN` 主要来自探索生命周期，而不是结构缺失。
- 下一轮应选择更贴近真实开发、研究或产品判断的探索主题，避免持续机制自证。

## Best Fit

- 本轮探索属于模板复用型探索。
- 它验证的是第二轮回流是否能被下一轮直接吸收，而不是验证业务功能或代码路径。

## Next Action

- 下一轮探索应选择一个真实项目议题，使用同一工作台模板验证 `Expected Evidence` 在非机制自检场景中的表现。
- 自动化延后条件保持不变：当后续至少两个探索样本出现重复的结构性 `WARN` 或 `MISSING` 时，再考虑新增只读检查脚本。
