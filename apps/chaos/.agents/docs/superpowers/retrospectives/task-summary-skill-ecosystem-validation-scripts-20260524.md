# 技能生态型基础设施校验脚本 Retrospective

## Outcome

- 本次探索交付了 4 个独立只读校验脚本，覆盖工作台完整性(`validate_workbench.py`)、技能合规性(`validate_skill_md.py`)、引用有效性(`validate_references.py`)与回流动作存在性(`validate_retro_feedback.py`)四个维度。
- 所有脚本零外部依赖，纯 Python stdlib，独立可运行。
- 对现有 11 个探索工作台、2 个技能 SKILL.md、4 个关键引用文件、29 个复盘文档执行了校验。
- 校验直接驱动了 3 处实质性规则/资产升级。

## Reused Foundation

- 完全复用探索协议页、探索工作台模板（含已升级的 checklist 骨架）、场景卡模板、复盘模板。
- 工作台启动过程未新增任何协议规则——第二轮闭环验证了"纯粹复用"模式成立。
- 代码风格复用了 `.agents/scripts/check_env.py` 的项目惯例（dataclass、Path、`from __future__ import annotations`）。

## Friction Points

- 首版脚本的 `validate_retro_feedback.py` 和 `validate_skill_md.py` 需要两轮修正才匹配真实文件的章节标题——正则匹配对模板章节命名的差异容忍度不足。
- `validate_references.py` 的交叉引用解析需要区分"相对于源文件目录"和"相对于项目根目录"两种路径语义，首版正确性依赖人工验证。
- `validate_workbench.py` 报告大量 MISSING 项，但大部分来自探索协议引入前创建的旧工作台——"柔性"校验脚本无法区分"历史合理缺失"和"结构性缺陷"。
- 4 个脚本仍需手工依次运行，无统一入口或汇总报告。

## Validation Result

- 低摩擦：成立。第二轮探索从场景卡到 spec 完全复用第一轮协议与模板，零新规则。
- 可复用：成立。4 个脚本独立可运行，下一轮探索可直接复用。
- 可回流：成立。校验结果驱动了协议页引用修复、citations.md 新增交叉引用完整性章节、skills.md 新增本地校验脚本引用。
- 可扩展：成立。新增一个校验维度只需新增一个独立脚本。

## Upgrade Recommendations

- 考虑添加 `validate_all.py` 作为统一入口，依次调用 4 个脚本并汇总退出码。
- 在复盘模板的 Next Action 章节中引入量化标准（至少一个可包含路径/文件名的具体动作），以便脚本更精确地判断"可执行"。
- `validate_workbench.py` 可增加时间戳判断——若 checklist.md 最后修改时间早于工作台模板的最后升级时间，则将 MISSING 降级为 INFO（历史兼容）。
- 技能生态型视图的"评测口径"字段在当前试点中未真正被脚本量化——建议下次技能生态型探索将其纳入校验逻辑。

## Best Fit

- 本轮探索属于技能生态型探索。
- 产出物（校验脚本）直接服务技能合规、引用完整性和回流动作检查，是典型的能力基础设施。

## Next Action

- 下一轮应选择一个比赛型或应用型探索主题，验证三类视图框架在非技能生态型场景下的适配能力。
- 本轮立即回流动作：4 个校验脚本 + 2 处规则升级 + 1 处协议页引用修复已完成；场景目录试点状态将在本文件归档后同步更新为"已完成"。
