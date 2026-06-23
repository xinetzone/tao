# Task 3: Create A Minimal Protocol Pilot Workbench

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

- `.agents/docs/superpowers/specs/agent-system/2026-05-24-agent-memory-dream-protocol-design.md`
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
