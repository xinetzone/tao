# Task 1: Verify The Protocol Asset Quartet

**Files:**
- Read: `.agents/docs/superpowers/specs/agent-system/2026-05-24-agent-memory-dream-protocol-design.md`
- Read: `.agents/docs/references/agent-memory-dream-protocol.md`
- Read: `.agents/docs/templates/agent-memory-entry-template.md`
- Read: `.agents/docs/templates/agent-dream-session-template.md`

- [ ] **Step 1: Confirm all four approved files exist**

Run:
```powershell
Test-Path .agents/docs/superpowers/specs/agent-system/2026-05-24-agent-memory-dream-protocol-design.md
Test-Path .agents/docs/references/agent-memory-dream-protocol.md
Test-Path .agents/docs/templates/agent-memory-entry-template.md
Test-Path .agents/docs/templates/agent-dream-session-template.md
```

Expected: all four commands print `True`.

- [ ] **Step 2: Verify the design spec contains the approved scope boundaries**

Run:
```powershell
Select-String -Path .agents/docs/superpowers/specs/agent-system/2026-05-24-agent-memory-dream-protocol-design.md -Pattern "不修改 `src/taolib/`|不实现 CLI 命令|不建立数据库或向量检索|不自动修改规则文件"
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
