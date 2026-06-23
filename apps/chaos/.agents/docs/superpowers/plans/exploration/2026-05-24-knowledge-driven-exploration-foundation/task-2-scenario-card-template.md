# Task 2: Upgrade The Shared Scenario Card Template

**Files:**
- Modify: `.agents/docs/templates/dao-scenario-card-template.md`

- [ ] **Step 1: Read the current scenario template before editing**

Run:
```bash
Get-Content .agents/docs/templates/dao-scenario-card-template.md
```

Expected: the file currently contains `Usage`、`Card Template`、`Validation Questions` and `Notes`.

- [ ] **Step 2: Replace the template with the exploration-ready version**

Replace the full contents of `.agents/docs/templates/dao-scenario-card-template.md` with exactly:
```md
# Dao Scenario Card Template

## Usage

用于把一个具体探索方向统一表达为“哲学 -> 产品 -> 技术 -> 验证 -> 复盘”的场景卡，并在同一张卡上支持比赛型、应用型与技能生态型三类轻量视图。

## Core Card Template

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

## Adaptation Views

### 比赛型探索

- 时间盒：
- 演示亮点：
- 评审价值：

### 应用型探索

- 用户价值：
- 能力边界：
- 阶段演进：

### 技能生态型探索

- 触发条件：
- 输入输出契约：
- 评测口径：

## Validation Questions

- 这个场景是否绑定了明确的哲学依据
- 这个场景是否抽象出了真实的产品能力
- 这个场景是否对应清晰的技术模块
- 这个场景是否定义了可观察的验证指标
- 这个场景是否识别了主要风险与偏差
- 这个场景是否预留了复盘回流路径
- 三类适配视图是否只做轻量补充，而没有复制一套新模板

## Notes

- 核心字段保持稳定，适配字段只补充差异化信息
- 若某场景需要更多上下文，应在独立 spec 中展开，而不是继续膨胀场景卡
- 所有字段都应能被人类和 AI 直接读取
```

- [ ] **Step 3: Verify the upgraded template**

Run:
```bash
Get-Content .agents/docs/templates/dao-scenario-card-template.md
```

Expected: the template contains `Core Card Template` and `Adaptation Views`, and still keeps `Validation Questions`.

- [ ] **Step 4: Run diagnostics on the template**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/dao-scenario-card-template.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/templates/dao-scenario-card-template.md
git commit -m "docs(agents): upgrade exploration scenario card template"
```
