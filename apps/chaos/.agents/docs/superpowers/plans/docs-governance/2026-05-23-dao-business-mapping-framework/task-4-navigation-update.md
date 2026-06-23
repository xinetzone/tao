# Task 4: Wire The Framework Into Existing Navigation

**Files:**
- Modify: `.agents/docs/README.md`
- Modify: `.agents/docs/references/README.md`
- Modify: `.agents/docs/references/dao-tech-foundation.md`

- [ ] **Step 1: Inspect the current navigation files before editing**

Run:
```bash
Get-Content .agents/docs/README.md
Get-Content .agents/docs/references/README.md
Get-Content .agents/docs/references/dao-tech-foundation.md
```

Expected: the docs README already links `dao-tech-foundation.md`; the references README currently lists reference entry files; the philosophy page does not yet contain direct execution-layer links.

- [ ] **Step 2: Update `.agents/docs/README.md` with framework and catalog entry points**

Edit the section `如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：` so it becomes exactly:
```md
如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：

1. 先看 [`references/dao-tech-foundation.md`](./references/dao-tech-foundation.md)
2. 再看 [`references/dao-business-mapping-framework.md`](./references/dao-business-mapping-framework.md)
3. 需要具体示例时看 [`references/dao-scenario-catalog.md`](./references/dao-scenario-catalog.md)
4. 需要设计历史时，再进入 [`superpowers/`](./superpowers/)
```

- [ ] **Step 3: Update `.agents/docs/references/README.md` with the two new entries**

Edit the `## 当前入口` list so it becomes exactly:
```md
## 当前入口

- [Dao Tech Foundation](./dao-tech-foundation.md)
- [Dao Business Mapping Framework](./dao-business-mapping-framework.md)
- [Dao Scenario Catalog](./dao-scenario-catalog.md)
- [Python](./python/README.md)
- [Podman](./podman/README.md)
- [mise](./mise/README.md)
```

- [ ] **Step 4: Update `.agents/docs/references/dao-tech-foundation.md` with execution-layer links**

Append this new section before `## Sources`:
```md
## Execution Layer

- 执行层框架入口：[`dao-business-mapping-framework.md`](./dao-business-mapping-framework.md)
- 首批示例场景：[`dao-scenario-catalog.md`](./dao-scenario-catalog.md)
- 场景模板：[`../templates/dao-scenario-card-template.md`](../templates/dao-scenario-card-template.md)
```

- [ ] **Step 5: Verify the final diff scope**

Run:
```bash
git diff -- .agents/docs/README.md .agents/docs/references/README.md .agents/docs/references/dao-tech-foundation.md
```

Expected: the diff only adds framework-related navigation and execution-layer links.

- [ ] **Step 6: Run diagnostics on all edited files**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/dao-tech-foundation.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 7: Commit**

```bash
git add .agents/docs/README.md .agents/docs/references/README.md .agents/docs/references/dao-tech-foundation.md
git commit -m "docs(agents): wire dao framework into navigation"
```
