# Task 3: Create The Example Scenario Catalog

**Files:**
- Create: `.agents/docs/references/dao-scenario-catalog.md`

- [ ] **Step 1: Re-read the approved design spec for example fidelity**

Run:
```bash
Get-Content .agents/docs/superpowers/specs/misc/2026-05-23-dao-business-mapping-framework-design.md
```

Expected: the spec lists three example directions: `智能体柔性协作编排`、`知识闭环与复盘驱动演进`、`业务能力最小闭环建模`.

- [ ] **Step 2: Create the catalog with the first three scenario cards**

Create `.agents/docs/references/dao-scenario-catalog.md` with exactly:
```md
# Dao Scenario Catalog

## Goal

存放首批代表性场景卡，证明“哲学原则 -> 产品能力 -> 技术模块 -> 验证指标 -> 业务场景”的映射框架可被实际复用。

## Included Scenarios

- 智能体柔性协作编排
- 知识闭环与复盘驱动演进
- 业务能力最小闭环建模

## Scenarios

### 场景：智能体柔性协作编排

- 场景目标：设计一套低侵入、可组合的 agent 协作方式，降低单一大流程的耦合度。
- 哲学依据：`弱者道之用`
- 工程解释：优先使用柔性接口、声明式规则和可替换编排，而不是刚性绑定的大一统执行流。
- 产品能力：按任务类型组合技能、工作流和知识入口，支持渐进扩展。
- 技术模块：`.agents/workflows/`、`.agents/rules/`、`.agents/skills/`
- 验证指标：新增场景接入所需改动范围小；不同能力能按边界独立演进；失败时可局部回退。
- 实施优先级：首批
- 风险与偏差：为了“统一”反而把不同能力重新耦合进单一流程。
- 复盘入口：`.agents/docs/superpowers/retrospectives/`

### 场景：知识闭环与复盘驱动演进

- 场景目标：建立“设计 -> 执行 -> 复盘 -> 再抽象”的知识循环，避免任务经验一次性流失。
- 哲学依据：`反者道之动`
- 工程解释：在流程中预留回看、纠偏和再次抽象的机制，将复盘视为系统演进的一部分。
- 产品能力：让设计文档、执行计划与复盘文档形成连续链路，支持长期学习。
- 技术模块：`.trae/`、`.agents/docs/superpowers/specs/`、`.agents/docs/superpowers/retrospectives/`
- 验证指标：任务结束后能快速追溯设计意图；复盘结果能反向更新长期规范；重复问题出现频率下降。
- 实施优先级：首批
- 风险与偏差：复盘沦为形式化总结，无法反馈到规则和设计层。
- 复盘入口：`.agents/docs/superpowers/retrospectives/`

### 场景：业务能力最小闭环建模

- 场景目标：面对一个新的业务问题时，优先抽象出最小可行能力闭环，而非预先设计复杂平台。
- 哲学依据：`大道至简`
- 工程解释：将复杂目标拆回最小必要能力、最短调用链和最清晰职责边界，优先形成可验证的最小闭环。
- 产品能力：快速抽象业务问题、识别首批能力单元、明确优先级和落地路径。
- 技术模块：具体模块按业务方向展开，可先落在 spec、plan 与能力拆解流程中。
- 验证指标：首版能力集合小而完整；没有为未确认需求引入多余抽象；实施路径明确且可分阶段推进。
- 实施优先级：首批
- 风险与偏差：把“简化”误解为“省略关键约束”，导致后续返工。
- 复盘入口：对应业务方向的 spec、plan 与 retrospective

## Related Files

- [`dao-business-mapping-framework.md`](./dao-business-mapping-framework.md)
- [`../templates/dao-scenario-card-template.md`](../templates/dao-scenario-card-template.md)
```

- [ ] **Step 3: Verify the catalog against the template**

Run:
```bash
Get-Content .agents/docs/references/dao-scenario-catalog.md
```

Expected: all three scenario cards follow the same field order as the scenario template.

- [ ] **Step 4: Run diagnostics on the catalog**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/dao-scenario-catalog.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/references/dao-scenario-catalog.md
git commit -m "docs(agents): add dao scenario catalog"
```
