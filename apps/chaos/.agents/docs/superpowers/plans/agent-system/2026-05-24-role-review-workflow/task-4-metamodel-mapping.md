# Task 4: 更新协作元模型参考页目录映射

**Files:**
- Modify: `.agents/docs/references/agent-collaboration-metamodel.md`

- [ ] **Step 1: 在目录映射表中增加 role-review 条目**

读取 `.agents/docs/references/agent-collaboration-metamodel.md`，找到 `## 7. 目录映射` 的表格。在 `.agents/workflows/` 行之前插入一行：

```markdown
| `.agents/workflows/role-review/` | Execution 域协作协议实例 | 首条多角色协作工作流，覆盖角色审批四道门禁。 |
```

修改后的完整表格应为：

```markdown
| 当前位置 | 协作模型定位 | 说明 |
|---|---|---|
| `AGENTS.md` | Governance Layer 总入口 | 全局治理契约、任务路由与协作边界。 |
| `.agents/rules/` | Governance Layer 规则实现 | 对 Role、Workflow、知识访问等对象的约束。 |
| `.agents/workflows/role-review/` | Execution 域协作协议实例 | 首条多角色协作工作流，覆盖角色审批四道门禁。 |
| `.agents/workflows/` | Execution 域协作协议实例 | 围绕任务执行的流程化编排说明。 |
| `.agents/skills/` | Knowledge 域能力资产 | 可被 Role 或 Agent 使用的能力单元。 |
| `.agents/roles/` | Organization 域实例承载 | 首字母义实例目录，当前试点 Role 实例。 |
| `.agents/docs/` | Knowledge 域长期知识层 | 规则、参考、洞见、spec、复盘等知识资产。 |
| `.trae/` | Runtime State 任务期工作台 | Session、草稿、执行中上下文与临时产物。 |
```

- [ ] **Step 2: 检查映射表没有重复条目**

Run:

```bash
git diff -- .agents/docs/references/agent-collaboration-metamodel.md
```

Expected: 仅新增一行 `.agents/workflows/role-review/`，其他条目不变。

- [ ] **Step 3: 提交**

```bash
git add .agents/docs/references/agent-collaboration-metamodel.md
git commit -m "docs(agent): add role-review to metamodel directory mapping"
```
