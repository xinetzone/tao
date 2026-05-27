# Exploration Reference Integrity Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 验证探索闭环中的关键引用关系是否能用低成本、只读方式被检查，并用上一轮试点完成一次手工验证。

**Architecture:** 本计划不引入脚本或自动修复逻辑，而是先把只读检查规则落为结构化文档，再用 `exploration-knowledge-loop-pilot` 作为样本执行一次手工检查。检查结果进入 `.temp/` 作为临时验证记录，最终复盘归档到 `.agents/docs/superpowers/retrospectives/` 并产生至少一个回流动作。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, `.trae` workspace structure, PowerShell, uv, pytest, pre-commit

---

## File Structure

- Read: `.trae/specs/exploration-reference-integrity-check/spec.md`
  - 作用：第二轮探索的设计边界与最小检查集合。
- Modify: `.trae/specs/exploration-reference-integrity-check/tasks.md`
  - 作用：记录本轮探索执行状态。
- Modify: `.trae/specs/exploration-reference-integrity-check/checklist.md`
  - 作用：记录本轮探索验收状态。
- Create: `.temp/exploration-reference-integrity-check.md`
  - 作用：临时手工检查记录；用于验证，不进入长期知识库。
- Create: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md`
  - 作用：本轮探索复盘与回流动作归档。
- Read: `.agents/docs/references/knowledge-driven-exploration-protocol.md`
  - 作用：确认协议页引用模板与试点工作台。
- Read: `.agents/docs/references/dao-scenario-catalog.md`
  - 作用：确认长期场景目录包含上一轮试点场景。
- Read: `.agents/docs/README.md`
  - 作用：确认 AI 文档导航包含探索协议或场景目录入口。
- Read: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-knowledge-loop-pilot.md`
  - 作用：确认上一轮复盘位置与 Next Action。

---

### Task 1: Confirm The Minimal Read-Only Check Set

**Files:**
- Read: `.trae/specs/exploration-reference-integrity-check/spec.md`
- Modify: `.trae/specs/exploration-reference-integrity-check/tasks.md`
- Modify: `.trae/specs/exploration-reference-integrity-check/checklist.md`

- [ ] **Step 1: Read the second-round spec**

Run:
```powershell
Get-Content .trae/specs/exploration-reference-integrity-check/spec.md
```

Expected: the spec contains `Minimal Reference Set` and `Check Status Semantics`.

- [ ] **Step 2: Confirm the six required checks**

Use this exact set for the manual validation:

```text
1. Protocol page exists and points to templates or the pilot workbench.
2. Scenario catalog contains the pilot scenario.
3. Pilot workbench contains spec.md, tasks.md, and checklist.md.
4. AI docs navigation points to the exploration protocol or scenario catalog.
5. Pilot retrospective is stored under .agents/docs/superpowers/retrospectives/.
6. Pilot retrospective contains Next Action with at least one executable feedback action.
```

Expected: no additional checks are added in this task.

- [ ] **Step 3: Keep tasks and checklist open until validation is complete**

Do not change checkbox states yet.

Expected: `tasks.md` and `checklist.md` remain pending before Task 2.

---

### Task 2: Run Manual Read-Only Validation Against The Pilot

**Files:**
- Create: `.temp/exploration-reference-integrity-check.md`
- Read: `.agents/docs/references/knowledge-driven-exploration-protocol.md`
- Read: `.agents/docs/references/dao-scenario-catalog.md`
- Read: `.agents/docs/README.md`
- Read: `.trae/specs/exploration-knowledge-loop-pilot/spec.md`
- Read: `.trae/specs/exploration-knowledge-loop-pilot/tasks.md`
- Read: `.trae/specs/exploration-knowledge-loop-pilot/checklist.md`
- Read: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-knowledge-loop-pilot.md`

- [ ] **Step 1: Create the temporary validation record**

Create `.temp/exploration-reference-integrity-check.md` with this exact initial content:

```md
# Exploration Reference Integrity Check

## Sample

- Topic: `exploration-knowledge-loop-pilot`
- Mode: manual read-only validation

## Status Semantics

- `PASS`: key file or reference exists and satisfies the minimum loop requirement.
- `WARN`: file exists but the relationship is indirect, weak, or semantically ambiguous.
- `MISSING`: key file, directory, section, or reference is absent.

## Results

| Check | Status | Evidence | Note |
|-------|--------|----------|------|
| Protocol page points to templates or pilot workbench | PASS | `.agents/docs/references/knowledge-driven-exploration-protocol.md` Related Files | Protocol page links templates and pilot workbench. |
| Scenario catalog contains pilot scenario | PASS | `.agents/docs/references/dao-scenario-catalog.md` | Catalog contains `探索任务知识闭环最小试点`. |
| Pilot workbench has spec/tasks/checklist | PASS | `.trae/specs/exploration-knowledge-loop-pilot/` | Required three-file workbench exists. |
| AI docs navigation points to exploration protocol or catalog | PASS | `.agents/docs/README.md` | Philosophy-driven path links protocol and scenario catalog. |
| Pilot retrospective is in retrospectives directory | PASS | `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-knowledge-loop-pilot.md` | File is in the required archive directory. |
| Pilot retrospective contains executable Next Action | PASS | `Next Action` section | Next action names a second skill-ecosystem exploration and an immediate checklist feedback action. |

## Friction Observed

- The checks are easy to perform manually, but evidence is spread across several files.
- The protocol page can point to a pilot workbench, but it does not explicitly name the retrospective file.
- Current `PASS` status is enough for the sample, but future samples may need `WARN` when references are indirect.

## Preliminary Conclusion

- Manual read-only checking is viable.
- Script automation is not required immediately.
- The next useful improvement is to add a stable expected-evidence section to the workbench template or exploration protocol.
```

Expected: the file exists under `.temp/`, not under `.agents/docs/`.

- [ ] **Step 2: Verify the temporary record contains all six checks**

Run:
```powershell
Get-Content .temp/exploration-reference-integrity-check.md
```

Expected: output contains all six result rows and at least one `Friction Observed` bullet.

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
.agents/docs/superpowers/plans/2026-05-24-exploration-reference-integrity-check.md
.temp/exploration-reference-integrity-check.md
.agents/docs/superpowers/retrospectives/2026-05-24-exploration-reference-integrity-check.md
```

Expected: user can review the second-round exploration and choose whether to execute it now.
