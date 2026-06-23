# Task 3: Create The Spec And Retrospective Templates

**Files:**
- Create: `.agents/docs/templates/knowledge-driven-exploration-spec-template.md`
- Create: `.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md`

- [ ] **Step 1: Inspect the approved design sections that must appear in the reusable templates**

Run:
```bash
Get-Content .agents/docs/superpowers/specs/misc/2026-05-24-knowledge-driven-exploration-foundation-design/index.md
```

Expected: the design clearly lists `Goal`、`Non-Goals`、`Architecture Layers`、`Protocol`、`Validation Model` and `Risks`.

- [ ] **Step 2: Create the spec template**

Create `.agents/docs/templates/knowledge-driven-exploration-spec-template.md` with exactly:
```md
# Knowledge-Driven Exploration Spec Template

## Usage

用于把一张探索场景卡展开为正式 spec，统一描述边界、核心能力闭环、阶段划分、验证标准与回流计划。

## Template

```md
# <主题>

## Goal

- 这次探索最终要证明什么

## Background

- 当前上下文
- 已有相关资产
- 为什么现在做

## Scope

- 本次要覆盖的内容

## Non-Goals

- 本次明确不做的内容

## Core Loop

- 场景卡如何进入 spec
- spec 如何进入计划
- 如何验证
- 如何复盘回流

## Layer Mapping

- 共性知识层：
- 场景适配层：
- 轻工作流层：
- 回流演化层：

## Deliverables

- 本次会产出哪些模板、页面、计划或试点

## Validation

- 低摩擦：
- 可复用：
- 可回流：
- 可扩展：

## Risks

- 主要风险
- 偏差路径

## Rollback Or Adjustment

- 如果试点失败，优先调整哪里

## Next Step

- 进入 plan 的条件
```

## Notes

- 首版优先保证字段稳定，不加入 PRD 级别的产品细节
- 如果探索内容超出一个闭环，应拆成多个 spec，而不是继续加章节
```

- [ ] **Step 3: Create the retrospective template**

Create `.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md` with exactly:
```md
# Knowledge-Driven Exploration Retrospective Template

## Usage

用于在一次探索闭环结束后，回答“哪些能力已复用、哪些地方仍然脆弱、哪些经验应该升级为底座资产”。

## Template

```md
# <主题> Retrospective

## Outcome

- 这次探索最终交付了什么

## Reused Foundation

- 复用了哪些协议、模板、工作台结构或导航资产

## Friction Points

- 哪些步骤仍然依赖手工
- 哪些约定容易被误解

## Validation Result

- 低摩擦：
- 可复用：
- 可回流：
- 可扩展：

## Upgrade Recommendations

- 哪些内容应该升级为模板
- 哪些内容应该进入参考页
- 哪些内容应该回写场景目录

## Best Fit

- 更适合比赛型、应用型还是技能生态型探索

## Next Action

- 下一轮应继续扩展什么
```

## Notes

- 复盘必须指向至少一个可执行的回流动作
- 复盘不是任务流水账，而是底座演化输入
```

- [ ] **Step 4: Verify both templates**

Run:
```bash
Get-Content .agents/docs/templates/knowledge-driven-exploration-spec-template.md
Get-Content .agents/docs/templates/knowledge-driven-exploration-retrospective-template.md
```

Expected: the spec template contains `Core Loop` and `Layer Mapping`; the retrospective template contains `Reused Foundation` and `Upgrade Recommendations`.

- [ ] **Step 5: Run diagnostics on both templates**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/knowledge-driven-exploration-spec-template.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/knowledge-driven-exploration-retrospective-template.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 6: Commit**

```bash
git add .agents/docs/templates/knowledge-driven-exploration-spec-template.md .agents/docs/templates/knowledge-driven-exploration-retrospective-template.md
git commit -m "docs(agents): add exploration spec and retrospective templates"
```
