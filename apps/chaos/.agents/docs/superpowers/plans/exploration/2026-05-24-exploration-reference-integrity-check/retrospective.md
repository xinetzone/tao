# Retrospective

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

本单元覆盖复盘记录阶段：归档第二轮探索复盘、标记工作台完成并验证探索产出。

---

### Task 3: Archive The Second-Round Retrospective

**Files:**
- Create: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md`
- Read: `.temp/exploration-reference-integrity-check.md`

- [ ] **Step 1: Create the retrospective**

Create `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md` with this exact content:

```md
# Exploration Reference Integrity Check Retrospective

## Outcome

- 本轮探索验证了探索闭环引用完整性可以先用手工只读方式检查，不需要立即脚本化。
- 使用 `exploration-knowledge-loop-pilot` 作为样本，完成了协议页、场景目录、工作台、导航入口、复盘位置与 Next Action 的六项检查。
- 六项检查在当前样本中均可判定为 `PASS`。

## Reused Foundation

- 复用了 `.agents/docs/references/knowledge-driven-exploration-protocol.md` 中的统一探索协议。
- 复用了 `.trae/specs/exploration-reference-integrity-check/` 作为第二轮探索工作台。
- 复用了上一轮试点的复盘结论，将“只读引用检查”作为真实技能生态型探索主题。

## Friction Points

- 证据分散在协议页、场景目录、导航入口、工作台与复盘文件之间，人工检查需要多次跳转。
- 协议页能够指向模板和试点工作台，但没有显式要求指向对应复盘文件。
- 当前 `PASS` 结果说明样本稳定，但还不足以证明所有未来探索都不需要脚本辅助。

## Validation Result

- 低摩擦：成立。六项检查可以通过阅读现有 Markdown 文件完成。
- 可复用：成立。检查集合可以用于下一轮探索主题。
- 可回流：成立。结果直接指向工作台模板或协议页的证据字段增强。
- 可扩展：部分成立。状态语义已经具备脚本化基础，但暂不需要立即实现脚本。

## Upgrade Recommendations

- 将“预期证据”字段加入探索工作台模板，明确每轮探索结束时应能指向协议页、场景目录、复盘与回流动作。
- 暂不新增自动化脚本，等至少第二个真实样本出现 `WARN` 或 `MISSING` 后再评估脚本化收益。
- 后续探索复盘中保留 `Next Action` 作为强制章节，继续要求至少一个可执行回流动作。

## Best Fit

- 本轮探索属于技能生态型探索。
- 它验证的是规则、模板、导航与复盘之间的知识资产关系，而不是业务功能或展示型原型。

## Next Action

- 下一轮回流动作：更新 `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md`，加入“预期证据”小节。
- 自动化延后条件：当后续至少两个探索样本出现重复的 `WARN` 或 `MISSING` 时，再考虑新增只读检查脚本。
```

Expected: retrospective exists under `.agents/docs/superpowers/retrospectives/`.

- [ ] **Step 2: Verify the retrospective contains a concrete Next Action**

Run:
```powershell
Select-String -Path .agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md -Pattern "Next Action|预期证据|自动化延后条件"
```

Expected: all three patterns appear in the output.

---

### Task 4: Mark The Second-Round Workbench Complete

**Files:**
- Modify: `.trae/specs/exploration-reference-integrity-check/tasks.md`
- Modify: `.trae/specs/exploration-reference-integrity-check/checklist.md`

- [ ] **Step 1: Update tasks.md to completed**

Replace the task list in `.trae/specs/exploration-reference-integrity-check/tasks.md` with:

```md
# Tasks
- [x] Task 1: 确认只读检查的最小引用集合。
- [x] Task 2: 使用上一轮试点完成手工检查记录。
- [x] Task 3: 根据检查结果输出复盘。
- [x] Task 4: 确认至少一个回流动作。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
```

Expected: all tasks use `[x]`.

- [ ] **Step 2: Update checklist.md to completed**

Replace the checklist in `.trae/specs/exploration-reference-integrity-check/checklist.md` with:

```md
- [x] 已定义最小必查引用集合
- [x] 已定义 `PASS`、`WARN`、`MISSING` 状态语义
- [x] 已使用 `exploration-knowledge-loop-pilot` 完成一次手工只读检查
- [x] 已记录至少一个真实摩擦点或稳定性结论
- [x] 已输出复盘并指定至少一个回流动作
```

Expected: all checklist items use `[x]`.

---

### Task 5: Verify The Exploration Outputs

**Files:**
- Read: `.temp/exploration-reference-integrity-check.md`
- Read: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md`
- Read: `.trae/specs/exploration-reference-integrity-check/tasks.md`
- Read: `.trae/specs/exploration-reference-integrity-check/checklist.md`

- [ ] **Step 1: Verify Git status**

Run:
```powershell
git status --short
```

Expected: output includes the new second-round workbench, the new plan, the new retrospective, and the `.temp/` validation record if `.temp/` is not ignored.

- [ ] **Step 2: Run the test suite**

Run:
```powershell
uv run pytest
```

Expected: all tests pass.

- [ ] **Step 3: Run pre-commit**

Run:
```powershell
uv run pre-commit run --all-files
```

Expected: command exits successfully.

- [ ] **Step 4: Summarize outputs**

Report these paths to the user:

```text
.trae/specs/exploration-reference-integrity-check/spec.md
.trae/specs/exploration-reference-integrity-check/tasks.md
.trae/specs/exploration-reference-integrity-check/checklist.md
.agents/docs/superpowers/plans/exploration/2026-05-24-exploration-reference-integrity-check/index.md
.temp/exploration-reference-integrity-check.md
.agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md
```

Expected: user can review the second-round exploration and choose whether to execute it now.
