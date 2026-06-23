# Task 4: Run Validation And Decide Whether To Produce A Retrospective

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
