# Task 2: Add The Reusable Scenario Card Template

**Files:**
- Create: `.agents/docs/templates/dao-scenario-card-template.md`

- [ ] **Step 1: Inspect the existing template style**

Run:
```bash
Get-Content .agents/docs/templates/reference-page-template.md
```

Expected: the current template uses compact Markdown sections and keyword-oriented headings.

- [ ] **Step 2: Create the scenario card template**

Create `.agents/docs/templates/dao-scenario-card-template.md` with exactly:
```md
# Dao Scenario Card Template

## Usage

用于把一个具体业务方向统一表达为“哲学 -> 产品 -> 技术 -> 验证 -> 复盘”的场景卡。

## Card Template

```md
### 场景：<名称>

- 场景目标：
- 哲学依据：
- 工程解释：
- 产品能力：
- 技术模块：
- 验证指标：
- 实施优先级：
- 风险与偏差：
- 复盘入口：
```

## Validation Questions

- 这个场景是否绑定了明确的哲学依据
- 这个场景是否抽象出了真实的产品能力
- 这个场景是否对应清晰的技术模块
- 这个场景是否定义了可观察的验证指标
- 这个场景是否识别了主要风险与偏差
- 这个场景是否预留了复盘回流路径

## Notes

- 首版优先保持卡片简洁，不增加额外字段
- 若某场景需要更多上下文，应在独立 spec 中展开，而不是污染模板
- 所有字段都应能被人类和 AI 直接读取
```

- [ ] **Step 3: Verify the template is readable and minimal**

Run:
```bash
Get-Content .agents/docs/templates/dao-scenario-card-template.md
```

Expected: the file contains `Card Template` and `Validation Questions`, and no extra placeholder sections.

- [ ] **Step 4: Run diagnostics on the template**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/dao-scenario-card-template.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/templates/dao-scenario-card-template.md
git commit -m "docs(agents): add dao scenario card template"
```
