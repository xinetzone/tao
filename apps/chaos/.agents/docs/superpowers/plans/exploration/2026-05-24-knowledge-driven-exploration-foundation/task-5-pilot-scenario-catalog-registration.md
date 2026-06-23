# Task 5: Register The Pilot In The Long-Term Scenario Catalog

**Files:**
- Modify: `.agents/docs/references/dao-scenario-catalog.md`

- [ ] **Step 1: Read the current scenario catalog before extending it**

Run:
```bash
Get-Content .agents/docs/references/dao-scenario-catalog.md
```

Expected: the catalog currently contains three scenario cards and a `Catalog Overview` table.

- [ ] **Step 2: Update the overview table with the pilot entry**

Edit the `Catalog Overview` table so it becomes exactly:
```md
| 场景 | 哲学依据 | 优先级 | 状态 |
|------|----------|--------|------|
| 智能体柔性协作编排 | 弱者道之用 | 首批 | 示例 |
| 知识闭环与复盘驱动演进 | 反者道之动 | 首批 | 示例 |
| 业务能力最小闭环建模 | 大道至简 | 首批 | 示例 |
| 探索任务知识闭环最小试点 | 反者道之动 | 当前 | 试点 |
```

- [ ] **Step 3: Append the pilot scenario card after `业务能力最小闭环建模`**

Append exactly this block to `.agents/docs/references/dao-scenario-catalog.md`:
```md
### 场景：探索任务知识闭环最小试点

- 场景目标：以最小成本验证探索型能力底座是否能够稳定串起“场景卡 -> spec -> plan -> 验证 -> 复盘 -> 回流”。
- 哲学依据：`反者道之动`
- 工程解释：先把一次探索跑成完整闭环，再决定哪些经验值得进入模板、协议或工作流，而不是提前平台化。
- 产品能力：让一个探索主题能够被稳定立项、执行、验证并回流为长期资产。
- 技术模块：`.agents/docs/references/knowledge-driven-exploration-protocol.md`、`.agents/docs/templates/`、`.trae/specs/exploration-knowledge-loop-pilot/`
- 验证指标：协议与模板能支撑真实试点；试点结束后至少有一条明确回流动作；下一次探索可直接复用本次资产。
- 实施优先级：当前
- 风险与偏差：如果试点只停留在模板创建而没有复盘回流，会误判底座已经成立。
- 复盘入口：`.agents/docs/superpowers/retrospectives/`
```

- [ ] **Step 4: Verify the catalog update**

Run:
```bash
Get-Content .agents/docs/references/dao-scenario-catalog.md
```

Expected: the overview table contains the pilot row, and the new pilot scenario card follows the same field order as the existing cards.

- [ ] **Step 5: Run diagnostics on the updated catalog**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/dao-scenario-catalog.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 6: Commit**

```bash
git add .agents/docs/references/dao-scenario-catalog.md
git commit -m "docs(agents): register exploration pilot scenario"
```
