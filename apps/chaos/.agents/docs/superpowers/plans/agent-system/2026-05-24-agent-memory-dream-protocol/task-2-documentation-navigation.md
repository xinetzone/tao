# Task 2: Add Discoverability To AI Documentation Navigation

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
