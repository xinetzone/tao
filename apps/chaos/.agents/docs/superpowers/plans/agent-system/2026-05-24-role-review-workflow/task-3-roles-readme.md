# Task 3: 更新 roles/README.md 角色清单

**Files:**
- Modify: `.agents/roles/README.md`

- [ ] **Step 1: 增加审查状态列并补充工作流引用**

读取当前 `.agents/roles/README.md`。将角色清单表更新为增加审查状态列，并在表格后补充工作流引用段。

更新角色清单表：

```markdown
## 当前角色清单

| 文件 | 角色 | 领域 | 审查状态 |
|---|---|---|---|
| `organization-steward.md` | Organization Steward | Organization | ✅ 已审查 |
| `execution-orchestrator.md` | Execution Orchestrator | Execution | ✅ 已审查 |
| `collaboration-architect.md` | Collaboration Architect | Governance + Knowledge | ✅ 已审查 |
| `governance-auditor.md` | Governance Auditor | Governance | ✅ 已审查 |
```

在角色清单表之后补充：

```markdown
## 审查流程

新增角色须通过 `.agents/workflows/role-review.md` 定义的四道门禁审批。提案模板见 `.agents/workflows/role-review/templates/proposal.md`。

当前四个角色已通过试运行自审查，审查记录见 `.agents/workflows/role-review/verification/`。
```

- [ ] **Step 2: 提交**

```bash
git add .agents/roles/README.md
git commit -m "docs(agent): add review status to roles manifest"
```
