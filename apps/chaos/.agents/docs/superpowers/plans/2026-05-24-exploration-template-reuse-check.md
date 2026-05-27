# Exploration Template Reuse Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 验证更新后的探索工作台模板是否能支撑新一轮探索，并确认 `Expected Evidence` 是否降低闭环证据收尾摩擦。

**Architecture:** 本计划继续采用文档驱动、只读验证优先的探索方式。第三轮工作台已位于 `.trae/specs/exploration-template-reuse-check/`，执行时只补充临时验证记录、复盘文件，并在 checklist/tasks 中反映完成状态。本轮不新增脚本，不修改产品代码。

**Tech Stack:** Markdown, Git, PowerShell, `uv run pytest`, `uv run pre-commit run --all-files`

---

### Task 1: Confirm Workbench Baseline

**Files:**
- Read: `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md`
- Read: `.trae/specs/exploration-template-reuse-check/spec.md`
- Read: `.trae/specs/exploration-template-reuse-check/tasks.md`
- Read: `.trae/specs/exploration-template-reuse-check/checklist.md`

- [ ] **Step 1: Read the updated workbench template**

Run:

```powershell
Get-Content .agents/docs/templates/knowledge-driven-exploration-workbench-template.md
```

Expected: the template contains an `Expected Evidence` section and checklist item requiring evidence links to protocol, scenario, workbench, retrospective, and feedback action.

- [ ] **Step 2: Read the third-round workbench files**

Run:

```powershell
Get-Content .trae/specs/exploration-template-reuse-check/spec.md
Get-Content .trae/specs/exploration-template-reuse-check/tasks.md
Get-Content .trae/specs/exploration-template-reuse-check/checklist.md
```

Expected: the workbench contains `spec.md`, `tasks.md`, and `checklist.md`, and the checklist includes the expected evidence item.

### Task 2: Create Manual Validation Record

**Files:**
- Create: `.temp/exploration-template-reuse-check.md`

- [ ] **Step 1: Ensure the temporary directory exists**

Run:

```powershell
New-Item -ItemType Directory -Force -Path .temp
```

Expected: `.temp` exists.

- [ ] **Step 2: Write the manual validation record**

Create `.temp/exploration-template-reuse-check.md` with this content:

```md
# Exploration Template Reuse Check

## Sample

- Sample topic: `exploration-template-reuse-check`
- Template source: `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md`
- Workbench path: `.trae/specs/exploration-template-reuse-check/`

## Check Results

| Check | Status | Evidence | Note |
|-------|--------|----------|------|
| Updated template exposes expected evidence requirements | PASS | `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md` | Template contains the `Expected Evidence` section. |
| Third-round workbench has spec/tasks/checklist | PASS | `.trae/specs/exploration-template-reuse-check/` | Required three-file workbench exists. |
| Spec declares goal, scope, non-goals, deliverables, and risks | PASS | `.trae/specs/exploration-template-reuse-check/spec.md` | The spec follows the current template skeleton. |
| Checklist carries expected evidence closure item | PASS | `.trae/specs/exploration-template-reuse-check/checklist.md` | The new checklist item is present. |
| Expected evidence can be listed during closure | WARN | Current workbench and planned retrospective | The retrospective does not exist until Task 3 completes. |
| Next Action can be captured in retrospective | WARN | Planned retrospective | The section will be validated after the retrospective is written. |

## Friction Points

- The updated template makes expected evidence visible before execution starts.
- During execution, retrospective-related evidence cannot be fully `PASS` until the retrospective file exists.
- The current checklist is useful, but closure status naturally moves from `WARN` to `PASS` only near the end of the round.

## Initial Conclusion

- `Expected Evidence` reduces planning ambiguity.
- Some evidence is lifecycle-dependent and should be expected to remain `WARN` until the retrospective is created.
```

Expected: the file records both immediate `PASS` checks and lifecycle-dependent `WARN` checks.

### Task 3: Write Retrospective and Close Workbench

**Files:**
- Create: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-template-reuse-check.md`
- Modify: `.trae/specs/exploration-template-reuse-check/tasks.md`
- Modify: `.trae/specs/exploration-template-reuse-check/checklist.md`

- [ ] **Step 1: Write the retrospective**

Create `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-template-reuse-check.md` with this content:

```md
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
```

Expected: the retrospective includes `Next Action` and distinguishes lifecycle-dependent `WARN` from structural problems.

- [ ] **Step 2: Mark tasks complete**

Replace `.trae/specs/exploration-template-reuse-check/tasks.md` with:

```md
# Tasks
- [x] Task 1: 使用更新后的模板创建第三轮工作台。
- [x] Task 2: 完成模板复用的最小只读验证记录。
- [x] Task 3: 根据验证结果输出复盘。
- [x] Task 4: 确认至少一个回流动作或延后条件。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
```

Expected: all tasks are marked complete.

- [ ] **Step 3: Mark checklist complete**

Replace `.trae/specs/exploration-template-reuse-check/checklist.md` with:

```md
- [x] 场景卡或场景来源已明确
- [x] spec 已完成并边界清晰
- [x] plan 已完成并可执行
- [x] 至少完成一次最小验证
- [x] 已输出复盘并指定回流动作
- [x] 预期证据已完整指向协议、场景、工作台、复盘与回流动作
```

Expected: checklist shows the round is closed.

### Task 4: Validate and Review

**Files:**
- Review: `.trae/specs/exploration-template-reuse-check/spec.md`
- Review: `.trae/specs/exploration-template-reuse-check/tasks.md`
- Review: `.trae/specs/exploration-template-reuse-check/checklist.md`
- Review: `.temp/exploration-template-reuse-check.md`
- Review: `.agents/docs/superpowers/retrospectives/2026-05-24-exploration-template-reuse-check.md`

- [ ] **Step 1: Run tests**

Run:

```powershell
uv run pytest
```

Expected: existing tests pass.

- [ ] **Step 2: Run pre-commit**

Run:

```powershell
uv run pre-commit run --all-files
```

Expected: all hooks pass.

- [ ] **Step 3: Review git status**

Run:

```powershell
git status --short
```

Expected: only the third-round workbench, plan, retrospective, and temporary validation record appear as changes.

## Self-Review

- Spec coverage: the plan covers workbench baseline, manual validation, retrospective, checklist closure, tests, and pre-commit.
- Placeholder scan: no `TBD`, `TODO`, or undefined future work remains in the execution steps.
- Scope check: the plan stays within documentation-driven exploration and does not introduce scripts or product code changes.
