# Agent Memory Dream Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将已确认的“记忆、做梦”知识协议从独立文档资产推进为可发现、可试用、可验证、可回流的 AgentForge 认知协议。

**Architecture:** 实施分为四个串联文档单元：先确认协议四件套已经存在并与设计一致，再把参考协议页接入 AI 文档导航，然后创建一个最小 `.trae` 试点工作台，最后用试点结果决定是否回流到规则、模板或参考页。整个过程只修改 `.agents/docs/` 与 `.trae/` 下的文档资产，不触碰 `src/taolib/` 运行时代码。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, `.trae` workspace structure, mise task runner, pre-commit

---

## File Structure

- Existing: `.agents/docs/superpowers/specs/2026-05-24-agent-memory-dream-protocol-design.md`
  - 作用：已批准的设计规格，是本计划的单一设计来源。
- Existing: `.agents/docs/references/agent-memory-dream-protocol.md`
  - 作用：稳定参考协议页，供未来智能体快速理解触发条件、输入输出与回流位置。
- Existing: `.agents/docs/templates/agent-memory-entry-template.md`
  - 作用：长期记忆条目模板，约束记忆字段和进入条件。
- Existing: `.agents/docs/templates/agent-dream-session-template.md`
  - 作用：做梦会话模板，约束输入记忆、重组问题、洞见候选、遗忘建议与回流动作。
- Modify: `.agents/docs/README.md`
  - 作用：把记忆做梦协议接入 AI 文档场景导航，降低未来检索成本。
- Modify: `.agents/docs/references/README.md`
  - 作用：把参考协议页加入 `references/` 当前入口列表。
- Create: `.trae/specs/agent-memory-dream-protocol-pilot/spec.md`
  - 作用：承载一次最小试点的执行期 spec，验证协议是否低摩擦、可回流、可遗忘。
- Create: `.trae/specs/agent-memory-dream-protocol-pilot/tasks.md`
  - 作用：承载试点任务列表与依赖关系。
- Create: `.trae/specs/agent-memory-dream-protocol-pilot/checklist.md`
  - 作用：承载试点验收清单。
- Future optional: `.agents/docs/superpowers/retrospectives/2026-05-24-agent-memory-dream-protocol-pilot.md`
  - 作用：试点完成后沉淀复盘。只有执行试点并形成结果后才创建。

---

### Task 1: Verify The Protocol Asset Quartet

**Files:**
- Read: `.agents/docs/superpowers/specs/2026-05-24-agent-memory-dream-protocol-design.md`
- Read: `.agents/docs/references/agent-memory-dream-protocol.md`
- Read: `.agents/docs/templates/agent-memory-entry-template.md`
- Read: `.agents/docs/templates/agent-dream-session-template.md`

- [ ] **Step 1: Confirm all four approved files exist**

Run:
```powershell
Test-Path .agents/docs/superpowers/specs/2026-05-24-agent-memory-dream-protocol-design.md
Test-Path .agents/docs/references/agent-memory-dream-protocol.md
Test-Path .agents/docs/templates/agent-memory-entry-template.md
Test-Path .agents/docs/templates/agent-dream-session-template.md
```

Expected: all four commands print `True`.

- [ ] **Step 2: Verify the design spec contains the approved scope boundaries**

Run:
```powershell
Select-String -Path .agents/docs/superpowers/specs/2026-05-24-agent-memory-dream-protocol-design.md -Pattern "不修改 `src/taolib/`|不实现 CLI 命令|不建立数据库或向量检索|不自动修改规则文件"
```

Expected: the output includes each non-goal from the approved design, confirming the implementation remains a knowledge-protocol task.

- [ ] **Step 3: Verify the reference page contains protocol triggers and gate rules**

Run:
```powershell
Select-String -Path .agents/docs/references/agent-memory-dream-protocol.md -Pattern "Memory Candidate Triggers|Dream Triggers|Gate Rules|Feedback Mapping"
```

Expected: the output includes all four section headings.

- [ ] **Step 4: Verify the memory template contains expiration and feedback fields**

Run:
```powershell
Select-String -Path .agents/docs/templates/agent-memory-entry-template.md -Pattern "Expiration Conditions|Feedback Suggestion|是否需要做梦重组"
```

Expected: the output confirms the template supports aging, feedback, and dream-session routing.

- [ ] **Step 5: Verify the dream template requires non-summary outputs**

Run:
```powershell
Select-String -Path .agents/docs/templates/agent-dream-session-template.md -Pattern "Patterns Found|Conflicts Found|Forgetting Suggestions|Insight Candidates|Feedback Suggestions"
```

Expected: the output includes all five sections, preventing dream sessions from degrading into plain summaries.

---

### Task 2: Add Discoverability To AI Documentation Navigation

**Files:**
- Modify: `.agents/docs/README.md`
- Modify: `.agents/docs/references/README.md`

- [ ] **Step 1: Inspect current AI docs navigation before editing**

Run:
```powershell
Get-Content .agents/docs/README.md
Get-Content .agents/docs/references/README.md
```

Expected: `.agents/docs/README.md` contains the philosophy-driven navigation block, and `.agents/docs/references/README.md` contains a `当前入口` list.

- [ ] **Step 2: Update `.agents/docs/README.md` philosophy navigation**

Modify the block under `如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：` so it becomes exactly:

```md
如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：

1. 先看 [`references/dao-tech-foundation.md`](./references/dao-tech-foundation.md)
2. 再看 [`references/dao-business-mapping-framework.md`](./references/dao-business-mapping-framework.md)
3. 需要探索协议时看 [`references/knowledge-driven-exploration-protocol.md`](./references/knowledge-driven-exploration-protocol.md)
4. 需要记忆、做梦、洞见回流与遗忘协议时看 [`references/agent-memory-dream-protocol.md`](./references/agent-memory-dream-protocol.md)
5. 需要具体示例时看 [`references/dao-scenario-catalog.md`](./references/dao-scenario-catalog.md)
6. 需要设计历史时，再进入 [`superpowers/`](./superpowers/)
```

Expected: the memory-dream protocol is discoverable from the existing philosophy and exploration navigation path.

- [ ] **Step 3: Update `.agents/docs/references/README.md` current entries**

Modify the `当前入口` list so it becomes exactly:

```md
## 当前入口

- [Dao Tech Foundation](./dao-tech-foundation.md)
- [Dao Business Mapping Framework](./dao-business-mapping-framework.md)
- [Knowledge-Driven Exploration Protocol](./knowledge-driven-exploration-protocol.md)
- [Agent Memory Dream Protocol](./agent-memory-dream-protocol.md)
- [Dao Scenario Catalog](./dao-scenario-catalog.md)
- [Python](./python/README.md)
- [Podman](./podman/README.md)
- [mise](./mise/README.md)
```

Expected: the reference wiki has a direct entry for `Agent Memory Dream Protocol`.

- [ ] **Step 4: Verify navigation links resolve as relative paths**

Run:
```powershell
Test-Path .agents/docs/references/agent-memory-dream-protocol.md
Select-String -Path .agents/docs/README.md -Pattern "agent-memory-dream-protocol.md"
Select-String -Path .agents/docs/references/README.md -Pattern "Agent Memory Dream Protocol"
```

Expected: `Test-Path` prints `True`, and both `Select-String` commands find the new navigation entry.

---

### Task 3: Create A Minimal Protocol Pilot Workbench

**Files:**
- Create: `.trae/specs/agent-memory-dream-protocol-pilot/spec.md`
- Create: `.trae/specs/agent-memory-dream-protocol-pilot/tasks.md`
- Create: `.trae/specs/agent-memory-dream-protocol-pilot/checklist.md`

- [ ] **Step 1: Create the pilot workbench directory**

Run:
```powershell
New-Item -ItemType Directory -Force .trae/specs/agent-memory-dream-protocol-pilot
```

Expected: the directory exists at `.trae/specs/agent-memory-dream-protocol-pilot`.

- [ ] **Step 2: Create the pilot spec**

Create `.trae/specs/agent-memory-dream-protocol-pilot/spec.md` with exactly:

```md
# Agent Memory Dream Protocol Pilot Spec

## Goal

验证“记忆、做梦”知识协议是否能在一次真实任务收尾中低摩擦使用，并判断它是否能产生可回流、可遗忘的洞见。

## Scope

- 使用一次已完成的文档协议任务作为输入材料。
- 从任务结果中提取 1 条记忆候选。
- 使用记忆条目模板判断是否进入长期记忆。
- 使用做梦会话模板进行一次最小做梦式归纳。
- 输出至少 1 条洞见候选、遗忘建议或回流建议。

## Non-Goals

- 不实现 CLI。
- 不修改 `src/taolib/`。
- 不自动写入长期记忆。
- 不修改全局规则。
- 不把当前任务进度当作长期记忆。

## Input Material

- `.agents/docs/superpowers/specs/2026-05-24-agent-memory-dream-protocol-design.md`
- `.agents/docs/references/agent-memory-dream-protocol.md`
- `.agents/docs/templates/agent-memory-entry-template.md`
- `.agents/docs/templates/agent-dream-session-template.md`

## Deliverables

- 一条记忆候选判断记录。
- 一次最小做梦会话记录。
- 一条可回流、可遗忘或可延后观察的洞见候选。
- 一份试点验收清单。

## Risks

- 试点可能只复述协议，没有产生洞见。
- 输入记忆数量过少，做梦会话可能过早。
- 如果输出不能回流，说明协议仍需补充触发和验收标准。
```

Expected: the pilot spec clearly states one minimal validation loop and preserves all non-goals.

- [ ] **Step 3: Create the pilot tasks**

Create `.trae/specs/agent-memory-dream-protocol-pilot/tasks.md` with exactly:

```md
# Tasks

- [ ] Task 1: 读取协议四件套并确认输入材料。
- [ ] Task 2: 从本次协议建设任务中提取 1 条记忆候选。
- [ ] Task 3: 用记忆条目模板判断候选是否适合进入长期记忆。
- [ ] Task 4: 用做梦会话模板完成一次最小归纳。
- [ ] Task 5: 判断洞见候选应回流、遗忘、合并还是延后观察。
- [ ] Task 6: 根据 checklist 完成试点验收。

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 4]
- [Task 6] depends on [Task 5]
```

Expected: tasks form a linear validation loop from reading inputs to final acceptance.

- [ ] **Step 4: Create the pilot checklist**

Create `.trae/specs/agent-memory-dream-protocol-pilot/checklist.md` with exactly:

```md
# Checklist

- [ ] 协议四件套均存在。
- [ ] 记忆候选明确说明未来复用价值。
- [ ] 记忆候选明确说明稳定性与适用范围。
- [ ] 记忆候选包含过期条件或复查条件。
- [ ] 做梦会话有明确输入记忆。
- [ ] 做梦会话至少产出一个模式、冲突、遗忘建议、演化建议或回流动作。
- [ ] 洞见候选明确标注回流位置、遗忘动作或延后观察理由。
- [ ] 试点未修改 `src/taolib/`。
- [ ] 试点未自动修改 `.agents/rules/`。
- [ ] 试点结果可用于决定下一阶段是否规则化或工具化。
```

Expected: checklist directly maps to the design validation criteria: low friction, reusable, feedback-ready, forgettable, evolvable.

- [ ] **Step 5: Verify pilot files exist and contain expected sections**

Run:
```powershell
Test-Path .trae/specs/agent-memory-dream-protocol-pilot/spec.md
Test-Path .trae/specs/agent-memory-dream-protocol-pilot/tasks.md
Test-Path .trae/specs/agent-memory-dream-protocol-pilot/checklist.md
Select-String -Path .trae/specs/agent-memory-dream-protocol-pilot/spec.md -Pattern "Goal|Non-Goals|Deliverables"
Select-String -Path .trae/specs/agent-memory-dream-protocol-pilot/tasks.md -Pattern "Task Dependencies"
Select-String -Path .trae/specs/agent-memory-dream-protocol-pilot/checklist.md -Pattern "协议四件套|做梦会话|洞见候选"
```

Expected: all `Test-Path` commands print `True`, and all `Select-String` commands find matching sections.

---

### Task 4: Run Validation And Decide Whether To Produce A Retrospective

**Files:**
- Read: `.trae/specs/agent-memory-dream-protocol-pilot/spec.md`
- Read: `.trae/specs/agent-memory-dream-protocol-pilot/tasks.md`
- Read: `.trae/specs/agent-memory-dream-protocol-pilot/checklist.md`
- Optional create after real execution: `.agents/docs/superpowers/retrospectives/2026-05-24-agent-memory-dream-protocol-pilot.md`

- [ ] **Step 1: Run project lint after documentation changes**

Run:
```powershell
mise run lint
```

Expected: environment check passes, pre-commit checks pass, Ruff checks pass, and Markdown whitespace/end-of-file checks pass.

- [ ] **Step 2: Inspect changed files before deciding next action**

Run:
```powershell
git status --short
git diff -- .agents/docs/README.md .agents/docs/references/README.md .trae/specs/agent-memory-dream-protocol-pilot/spec.md .trae/specs/agent-memory-dream-protocol-pilot/tasks.md .trae/specs/agent-memory-dream-protocol-pilot/checklist.md
```

Expected: changes are limited to navigation and the pilot workbench files.

- [ ] **Step 3: Decide whether retrospective evidence exists**

Use this decision rule:

```text
If the pilot has actually produced a memory candidate, a dream-session result, and a feedback/forgetting decision, create a retrospective.
If the pilot workbench has only been scaffolded and not executed, do not create a retrospective yet.
```

Expected: no retrospective is created for scaffold-only work.

- [ ] **Step 4: Create retrospective only after executing the pilot**

If the pilot has real results, create `.agents/docs/superpowers/retrospectives/2026-05-24-agent-memory-dream-protocol-pilot.md` with exactly this structure and fill each bullet with the actual pilot result:

```md
# Agent Memory Dream Protocol Pilot Retrospective

## Summary

- 试点输入：
- 试点输出：
- 结论：

## Memory Candidate

- 候选内容：
- 复用价值：
- 稳定性：
- 过期条件：

## Dream Session Result

- 输入记忆：
- 发现的模式：
- 发现的冲突：
- 遗忘建议：
- 洞见候选：

## Feedback Decision

- 回流位置：
- 回流动作：
- 暂不回流理由：

## Protocol Adjustment

- 需要更新的模板：
- 需要更新的参考页：
- 需要更新的规则：
- 不需要调整的部分：

## Next Action

- 下一步：
```

Expected: retrospective is only created when each field can be filled with concrete pilot evidence.

- [ ] **Step 5: Final validation**

Run:
```powershell
mise run lint
```

Expected: lint remains green after optional retrospective creation.

- [ ] **Step 6: Commit only if explicitly requested by the user**

Do not run `git commit` unless the user explicitly asks for a commit.

If the user explicitly requests a commit, run:
```powershell
git add .agents/docs/README.md .agents/docs/references/README.md .trae/specs/agent-memory-dream-protocol-pilot
if (Test-Path .agents/docs/superpowers/retrospectives/2026-05-24-agent-memory-dream-protocol-pilot.md) { git add .agents/docs/superpowers/retrospectives/2026-05-24-agent-memory-dream-protocol-pilot.md }
git commit -m "docs(agents): operationalize memory dream protocol"
```

Expected: commit is created only after explicit user approval.

---

## Self-Review

### Spec Coverage

- 设计中的“知识协议层、不触碰运行时代码”由 Task 1 和 Task 4 的 non-goal 检查覆盖。
- 设计中的“可发现、可回流”由 Task 2 导航接入和 Task 4 回流决策覆盖。
- 设计中的“至少一次真实任务验证”由 Task 3 的 `.trae` 试点工作台和 Task 4 的执行/复盘判定覆盖。
- 设计中的“可遗忘”由 Task 3 checklist 与 Task 4 retrospective 的遗忘建议字段覆盖。

### Placeholder Scan

本计划不包含 `TBD`、`TODO`、`implement later` 或未定义的文件路径。可选复盘文件只在试点实际产生证据后创建，并明确了不创建条件。

### Consistency Check

所有路径均使用项目相对路径；所有执行命令均使用 PowerShell 兼容语法；提交步骤受到“用户明确要求后才提交”的约束。
