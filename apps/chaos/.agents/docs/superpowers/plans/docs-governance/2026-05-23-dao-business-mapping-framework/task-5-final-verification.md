# Task 5: Final Verification And Handoff

**Files:**
- Modify: `.agents/docs/references/dao-business-mapping-framework.md`
- Modify: `.agents/docs/templates/dao-scenario-card-template.md`
- Modify: `.agents/docs/references/dao-scenario-catalog.md`
- Modify: `.agents/docs/README.md`
- Modify: `.agents/docs/references/README.md`
- Modify: `.agents/docs/references/dao-tech-foundation.md`

- [ ] **Step 1: Read all framework files together**

Run:
```bash
Get-Content .agents/docs/references/dao-business-mapping-framework.md
Get-Content .agents/docs/templates/dao-scenario-card-template.md
Get-Content .agents/docs/references/dao-scenario-catalog.md
Get-Content .agents/docs/README.md
Get-Content .agents/docs/references/README.md
Get-Content .agents/docs/references/dao-tech-foundation.md
```

Expected: the files form a coherent chain of `philosophy foundation -> framework -> template -> scenario examples -> navigation`.

- [ ] **Step 2: Scan for placeholders and ambiguous markers**

Run:
```bash
Select-String -Path .agents/docs/references/dao-business-mapping-framework.md,.agents/docs/templates/dao-scenario-card-template.md,.agents/docs/references/dao-scenario-catalog.md,.agents/docs/README.md,.agents/docs/references/README.md,.agents/docs/references/dao-tech-foundation.md -Pattern "[T]BD|[T]ODO|待补|占位|未定"
```

Expected: no matches.

- [ ] **Step 3: Run a final repository status check**

Run:
```bash
git status --short
```

Expected: only the intended framework-related doc changes are present before the final commit, or the worktree is clean if all earlier commits were made.

- [ ] **Step 4: Write the handoff summary**

Prepare this summary for the final response:
```md
**已完成**
- 新增稳定框架参考页
- 新增场景卡模板
- 新增首批示例场景库
- 打通哲学总纲、执行层框架与导航入口

**建议下一步**
- 基于 `dao-scenario-catalog.md` 选择一个场景，展开为独立 spec
- 任务完成后将结果归档到 `retrospectives/` 并回流到框架文档
```

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/references/dao-business-mapping-framework.md .agents/docs/templates/dao-scenario-card-template.md .agents/docs/references/dao-scenario-catalog.md .agents/docs/README.md .agents/docs/references/README.md .agents/docs/references/dao-tech-foundation.md
git commit -m "docs(agents): finalize dao business mapping framework assets"
```
