# Tasks

- [x] Task 1: 校验场景卡字段完整性，确认 `dao-scenario-catalog.md` 中新增条目无缺失
- [x] Task 2: 确认 spec.md 边界清晰，四层映射与 Non-Goals 无遗漏
- [x] Task 3: 盘点三轮复盘的 WARN/MISSING 项，输出校验维度清单
- [x] Task 4: 实现 `validate-workbench.py`：检查工作台三文件结构完整性 + checklist/tasks 状态一致性
- [x] Task 5: 实现 `validate-skill-md.py`：检查 SKILL.md 7 个必填章节
- [x] Task 6: 实现 `validate-references.py`：检查交叉引用有效性
- [x] Task 7: 实现 `validate-retro-feedback.py`：检查复盘是否包含可执行回流动作
- [x] Task 8: 对现有 4 轮探索工作台 + 2 个技能的 SKILL.md 执行全部 4 个脚本
- [x] Task 9: 输出校验执行报告（Markdown）
- [x] Task 10: 根据校验结果升级至少一条规则（skills.md 或 citations.md）
- [x] Task 11: 输出复盘文档到 `.agents/docs/superpowers/retrospectives/2026-05-24-skill-ecosystem-validation-scripts.md`
- [x] Task 12: 更新 `dao-scenario-catalog.md` 中本场景状态为"已完成"

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 3]
- [Task 6] depends on [Task 3]
- [Task 7] depends on [Task 3]
- [Task 8] depends on [Task 4], [Task 5], [Task 6], [Task 7]
- [Task 9] depends on [Task 8]
- [Task 10] depends on [Task 9]
- [Task 11] depends on [Task 10]
- [Task 12] depends on [Task 11]
