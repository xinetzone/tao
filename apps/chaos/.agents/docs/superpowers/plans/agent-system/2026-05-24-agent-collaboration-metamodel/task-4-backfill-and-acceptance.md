### Task 4: 回填引用与验收校验

**Files:**
- Read: `AGENTS.md`
- Read: `.agents/README.md`
- Read: `.agents/docs/references/agent-collaboration-metamodel.md`
- Read: `.agents/roles/README.md`
- Read: `.agents/roles/collaboration-architect.md`

- [ ] **Step 1: 检查无占位词**

Run:


```bash
rg "TODO|TBD|待定|占位" AGENTS.md .agents/README.md .agents/docs/references/agent-collaboration-metamodel.md .agents/roles/README.md .agents/roles/collaboration-architect.md
```

Expected: 无匹配结果。

- [ ] **Step 2: 检查项目内链接均为相对路径**

手动确认以下链接形式存在且正确：

```text
./roles/
./docs/references/agent-collaboration-metamodel.md
.agents/roles/
.agents/docs/references/agent-collaboration-metamodel.md
```

- [ ] **Step 3: 检查 Mermaid 图仅使用基础语法**

手动确认仅使用：

```text
flowchart TD
flowchart LR
```

不引入复杂主题配置或不兼容语法。

- [ ] **Step 4: 检查改动范围**

Run:

```bash
git status --short
```

Expected: 只包含本计划涉及文件，或明确保留用户已有改动；不得误改 `src/taolib/`。

- [ ] **Step 5: Final Commit**

```bash
git add AGENTS.md .agents/README.md .agents/docs/references/agent-collaboration-metamodel.md .agents/roles/README.md .agents/roles/collaboration-architect.md
git commit -m "feat(agent): introduce collaboration model entrypoints"
```
