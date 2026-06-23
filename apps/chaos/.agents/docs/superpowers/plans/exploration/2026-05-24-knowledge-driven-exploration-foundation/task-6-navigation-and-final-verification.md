# Task 6: Wire Navigation And Run Final Verification

**Files:**
- Modify: `.agents/docs/README.md`
- Modify: `.agents/docs/references/README.md`
- Modify: `.agents/docs/references/knowledge-driven-exploration-protocol.md`
- Modify: `.agents/docs/templates/dao-scenario-card-template.md`
- Modify: `.agents/docs/templates/knowledge-driven-exploration-spec-template.md`
- Modify: `.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md`
- Modify: `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md`
- Modify: `.agents/docs/references/dao-scenario-catalog.md`
- Modify: `.trae/specs/exploration-knowledge-loop-pilot/spec.md`
- Modify: `.trae/specs/exploration-knowledge-loop-pilot/tasks.md`
- Modify: `.trae/specs/exploration-knowledge-loop-pilot/checklist.md`

- [ ] **Step 1: Update `.agents/docs/README.md` with the exploration protocol entry**

Edit the section `如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：` so it becomes exactly:
```md
如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：

1. 先看 [`references/dao-tech-foundation.md`](./references/dao-tech-foundation.md)
2. 再看 [`references/dao-business-mapping-framework.md`](./references/dao-business-mapping-framework.md)
3. 需要探索协议时看 [`references/knowledge-driven-exploration-protocol.md`](./references/knowledge-driven-exploration-protocol.md)
4. 需要具体示例时看 [`references/dao-scenario-catalog.md`](./references/dao-scenario-catalog.md)
5. 需要设计历史时，再进入 [`superpowers/`](./superpowers/)
```

- [ ] **Step 2: Update `.agents/docs/references/README.md` with the new protocol page**

Edit the `## 当前入口` list so it becomes exactly:
```md
## 当前入口

- [Dao Tech Foundation](./dao-tech-foundation.md)
- [Dao Business Mapping Framework](./dao-business-mapping-framework.md)
- [Knowledge-Driven Exploration Protocol](./knowledge-driven-exploration-protocol.md)
- [Dao Scenario Catalog](./dao-scenario-catalog.md)
- [Python](./python/README.md)
- [Podman](./podman/README.md)
- [mise](./mise/README.md)
```

- [ ] **Step 3: Verify the whole exploration chain together**

Run:
```bash
Get-Content .agents/docs/references/knowledge-driven-exploration-protocol.md
Get-Content .agents/docs/templates/dao-scenario-card-template.md
Get-Content .agents/docs/templates/knowledge-driven-exploration-spec-template.md
Get-Content .agents/docs/templates/knowledge-driven-exploration-retrospective-template.md
Get-Content .agents/docs/templates/knowledge-driven-exploration-workbench-template.md
Get-Content .agents/docs/references/dao-scenario-catalog.md
Get-Content .agents/docs/README.md
Get-Content .agents/docs/references/README.md
Get-Content .trae/specs/exploration-knowledge-loop-pilot/spec.md
Get-Content .trae/specs/exploration-knowledge-loop-pilot/tasks.md
Get-Content .trae/specs/exploration-knowledge-loop-pilot/checklist.md
```

Expected: the files form a coherent chain of `协议页 -> 场景卡模板 -> spec 模板 -> retrospective 模板 -> workbench 模板 -> 试点工作台 -> 长期场景目录 -> 导航入口`.

- [ ] **Step 4: Scan all exploration assets for placeholders**

Run:
```bash
Select-String -Path .agents/docs/references/knowledge-driven-exploration-protocol.md,.agents/docs/templates/dao-scenario-card-template.md,.agents/docs/templates/knowledge-driven-exploration-spec-template.md,.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md,.agents/docs/templates/knowledge-driven-exploration-workbench-template.md,.agents/docs/references/dao-scenario-catalog.md,.agents/docs/README.md,.agents/docs/references/README.md,.trae/specs/exploration-knowledge-loop-pilot/spec.md,.trae/specs/exploration-knowledge-loop-pilot/tasks.md,.trae/specs/exploration-knowledge-loop-pilot/checklist.md -Pattern "[T]BD|[T]ODO|待补|占位|未定"
```

Expected: no matches outside intentional template placeholders such as `<名称>` or `<主题>`.

- [ ] **Step 5: Run diagnostics on the edited Markdown files**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/knowledge-driven-exploration-protocol.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/dao-scenario-card-template.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/knowledge-driven-exploration-spec-template.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/knowledge-driven-exploration-workbench-template.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/dao-scenario-catalog.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.trae/specs/exploration-knowledge-loop-pilot/spec.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.trae/specs/exploration-knowledge-loop-pilot/tasks.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.trae/specs/exploration-knowledge-loop-pilot/checklist.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 6: Check the final repository status**

Run:
```bash
git status --short
```

Expected: only the intended exploration foundation files are modified or created before the final commit, or the worktree is clean if earlier commits were made.

- [ ] **Step 7: Commit**

```bash
git add .agents/docs/README.md .agents/docs/references/README.md .agents/docs/references/knowledge-driven-exploration-protocol.md .agents/docs/templates/dao-scenario-card-template.md .agents/docs/templates/knowledge-driven-exploration-spec-template.md .agents/docs/templates/knowledge-driven-exploration-retrospective-template.md .agents/docs/templates/knowledge-driven-exploration-workbench-template.md .agents/docs/references/dao-scenario-catalog.md .trae/specs/exploration-knowledge-loop-pilot/spec.md .trae/specs/exploration-knowledge-loop-pilot/tasks.md .trae/specs/exploration-knowledge-loop-pilot/checklist.md
git commit -m "docs(exploration): finalize knowledge-driven exploration foundation"
```
