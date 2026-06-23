# Task 5: 验收校验

**Files:**
- Read: `.agents/workflows/role-review.md`
- Read: `.agents/workflows/role-review/templates/proposal.md`
- Read: `.agents/workflows/role-review/verification/gate-01-organization-steward.md`
- Read: `.agents/workflows/role-review/verification/gate-02-execution-orchestrator.md`
- Read: `.agents/workflows/role-review/verification/gate-03-collaboration-architect.md`
- Read: `.agents/workflows/role-review/verification/gate-04-governance-auditor.md`
- Read: `.agents/roles/README.md`
- Read: `.agents/docs/references/agent-collaboration-metamodel.md`

- [ ] **Step 1: 全面占位词检查**

Run:

```bash
rg "TODO|TBD|待定|占位" .agents/workflows/role-review.md .agents/workflows/role-review/templates/ .agents/workflows/role-review/verification/ .agents/roles/README.md .agents/docs/references/agent-collaboration-metamodel.md
```

Expected: 无匹配结果。

- [ ] **Step 2: 检查所有文件 Mermaid 语法**

手动确认所有 Mermaid 块仅使用 `flowchart TD` 或 `flowchart LR`。

- [ ] **Step 3: 检查所有项目内链接**

手动确认以下链接存在且正确：
- `.agents/workflows/role-review.md` 中 `role-review/templates/proposal.md`
- `.agents/workflows/role-review.md` 中 `.agents/docs/references/agent-collaboration-metamodel.md`
- `.agents/roles/README.md` 中 `collaboration-architect.md` 等角色文件引用
- `.agents/roles/README.md` 中 `.agents/workflows/role-review.md`

- [ ] **Step 4: 检查改动范围**

Run:

```bash
git status --short
```

Expected: 仅包含本计划涉及的 8 个文件，不包含 `src/taolib/`。

- [ ] **Step 5: 最终提交**

如果 Task 1-4 已分批提交完毕，此步骤应为空提交，仅做最终确认。如还有未提交的改动：

```bash
git add -A
git commit -m "feat(agent): complete role review workflow implementation"
```

如已全部提交，运行：

```bash
git log --oneline -6
```

Expected: 最近 6 个提交覆盖全部 Task。
