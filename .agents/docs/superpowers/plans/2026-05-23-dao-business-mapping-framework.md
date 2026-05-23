# Dao Business Mapping Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将《道德经》哲学到业务落地的全链路框架，从设计稿转化为仓库中的稳定参考资产、可复用模板、示例场景库与导航入口。

**Architecture:** 实施分为四个独立但串联的文档单元。先把设计稿提炼为稳定参考页，再补充可复用模板与示例场景库，最后把这些资产接入现有导航与哲学总纲，形成“参考解释 -> 场景执行 -> 导航检索”的闭环。整个过程只修改 `.agents/docs/` 范围内的 AI 文档资产，不触碰人类文档树。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, VS Code diagnostics, Git

---

## File Structure

- Create: `.agents/docs/references/dao-business-mapping-framework.md`
  - 作用：沉淀稳定版的全链路框架说明，作为后续 AI 与人类共同引用的主入口。
- Create: `.agents/docs/templates/dao-scenario-card-template.md`
  - 作用：提供标准场景卡模板，供后续 spec、plan、retrospective 复用。
- Create: `.agents/docs/references/dao-scenario-catalog.md`
  - 作用：存放首批 3 个示例场景，证明框架可跨层复用。
- Modify: `.agents/docs/README.md`
  - 作用：接入新框架与场景库入口。
- Modify: `.agents/docs/references/README.md`
  - 作用：将新参考页和场景库加入 `references/` 导航。
- Modify: `.agents/docs/references/dao-tech-foundation.md`
  - 作用：将哲学总纲与执行层框架互相链接，避免两份文档割裂。

---

### Task 1: Create The Stable Framework Reference Page

**Files:**
- Create: `.agents/docs/references/dao-business-mapping-framework.md`

- [ ] **Step 1: Inspect the current philosophy reference for reuse boundaries**

Run:
```bash
Get-Content .agents/docs/references/dao-tech-foundation.md
```

Expected: the file already contains `Key Concepts`、`Transformation Path`、`Philosophy To Engineering Mapping` and should remain the philosophy-oriented source of truth.

- [ ] **Step 2: Create the new stable framework page**

Create `.agents/docs/references/dao-business-mapping-framework.md` with exactly:
```md
# Dao Business Mapping Framework

## Search Keywords

- 主关键词：业务场景映射、哲学到技术、全链路框架、场景矩阵、验证清单
- 英文术语：business mapping framework, scenario matrix, validation checklist, philosophy-to-engineering
- 常见别名：道家业务框架、场景映射母版、业务转化框架
- 错误短语：无

## Goal

说明如何把《道德经》的哲学原则稳定转化为产品能力、技术模块、验证指标与业务场景，并为后续 spec、plan 与 retrospective 提供统一表达骨架。

## Relevance In AgentForge

- 关联模块：`AGENTS.md`、`.agents/docs/references/dao-tech-foundation.md`、`.agents/docs/templates/`、`.agents/docs/superpowers/`
- 常见触发场景：设计新方向、抽象业务能力、拆解技术方案、建立验证标准、沉淀复盘
- 优先检查文件：`AGENTS.md`、`.agents/docs/references/dao-tech-foundation.md`

## Trigger Phrases

- 如何把哲学原则转成业务能力
- 怎样用统一模板描述一个业务场景
- 这条方案如何验证是否符合大道至简
- 如何从哲学一路落到技术和复盘

## Core Chain

```mermaid
flowchart LR
    A["哲学原则"] --> B["产品能力"]
    B --> C["技术模块"]
    C --> D["验证指标"]
    D --> E["业务场景"]
    E --> F["复盘反馈"]
    F --> A
```

## Layer Definitions

- `哲学原则`：定义价值取向与设计判断准绳。
- `产品能力`：把哲学转成业务和用户可感知的能力单元。
- `技术模块`：把能力进一步落成模块、规则、工作流、技能或数据结构。
- `验证指标`：定义可观察的成功标准。
- `业务场景`：放入真实问题空间验证前四层是否成立。
- `复盘反馈`：将执行结果回流到抽象层，形成纠偏与再设计。

## Standard Mapping Unit

- `哲学命题`
- `工程解释`
- `对应能力`
- `技术落点`
- `验证方法`
- `适用场景`

## Validation Checklist

- 是否绑定了明确的哲学依据，而不是抽象口号
- 是否抽象出了独立、可感知的产品能力
- 是否映射到清晰的技术模块，而不是职责混杂
- 是否定义了可观察的验证指标
- 是否识别了风险与偏差路径
- 是否预留了复盘和纠偏入口

## Recommended Usage

1. 先阅读 `dao-tech-foundation.md` 理解哲学内核
2. 再使用本页的链路和检查项进行方案设计
3. 使用 `dao-scenario-card-template.md` 编写具体场景
4. 将代表性场景沉淀到 `dao-scenario-catalog.md`
5. 任务结束后在 `retrospectives/` 中复盘并回流

## Related Files

- [`dao-tech-foundation.md`](./dao-tech-foundation.md)
- [`dao-scenario-catalog.md`](./dao-scenario-catalog.md)
- [`../templates/dao-scenario-card-template.md`](../templates/dao-scenario-card-template.md)

## Sources

- 设计来源：`.agents/docs/superpowers/specs/2026-05-23-dao-business-mapping-framework-design.md`
- 版本：2026-05-23
- 抓取时间：不适用
```

- [ ] **Step 3: Verify the new page content**

Run:
```bash
Get-Content .agents/docs/references/dao-business-mapping-framework.md
```

Expected: the file contains `Core Chain`、`Layer Definitions`、`Standard Mapping Unit` and `Validation Checklist`.

- [ ] **Step 4: Run diagnostics on the new page**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/dao-business-mapping-framework.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/references/dao-business-mapping-framework.md
git commit -m "docs(agents): add dao business mapping framework reference"
```

---

### Task 2: Add The Reusable Scenario Card Template

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

---

### Task 3: Create The Example Scenario Catalog

**Files:**
- Create: `.agents/docs/references/dao-scenario-catalog.md`

- [ ] **Step 1: Re-read the approved design spec for example fidelity**

Run:
```bash
Get-Content .agents/docs/superpowers/specs/2026-05-23-dao-business-mapping-framework-design.md
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

---

### Task 4: Wire The Framework Into Existing Navigation

**Files:**
- Modify: `.agents/docs/README.md`
- Modify: `.agents/docs/references/README.md`
- Modify: `.agents/docs/references/dao-tech-foundation.md`

- [ ] **Step 1: Inspect the current navigation files before editing**

Run:
```bash
Get-Content .agents/docs/README.md
Get-Content .agents/docs/references/README.md
Get-Content .agents/docs/references/dao-tech-foundation.md
```

Expected: the docs README already links `dao-tech-foundation.md`; the references README currently lists reference entry files; the philosophy page does not yet contain direct execution-layer links.

- [ ] **Step 2: Update `.agents/docs/README.md` with framework and catalog entry points**

Edit the section `如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：` so it becomes exactly:
```md
如果你需要理解项目的哲学驱动、极简原则与“理论 -> 技术 -> 业务”的转化路径：

1. 先看 [`references/dao-tech-foundation.md`](./references/dao-tech-foundation.md)
2. 再看 [`references/dao-business-mapping-framework.md`](./references/dao-business-mapping-framework.md)
3. 需要具体示例时看 [`references/dao-scenario-catalog.md`](./references/dao-scenario-catalog.md)
4. 需要设计历史时，再进入 [`superpowers/`](./superpowers/)
```

- [ ] **Step 3: Update `.agents/docs/references/README.md` with the two new entries**

Edit the `## 当前入口` list so it becomes exactly:
```md
## 当前入口

- [Dao Tech Foundation](./dao-tech-foundation.md)
- [Dao Business Mapping Framework](./dao-business-mapping-framework.md)
- [Dao Scenario Catalog](./dao-scenario-catalog.md)
- [Python](./python/README.md)
- [Podman](./podman/README.md)
- [mise](./mise/README.md)
```

- [ ] **Step 4: Update `.agents/docs/references/dao-tech-foundation.md` with execution-layer links**

Append this new section before `## Sources`:
```md
## Execution Layer

- 执行层框架入口：[`dao-business-mapping-framework.md`](./dao-business-mapping-framework.md)
- 首批示例场景：[`dao-scenario-catalog.md`](./dao-scenario-catalog.md)
- 场景模板：[`../templates/dao-scenario-card-template.md`](../templates/dao-scenario-card-template.md)
```

- [ ] **Step 5: Verify the final diff scope**

Run:
```bash
git diff -- .agents/docs/README.md .agents/docs/references/README.md .agents/docs/references/dao-tech-foundation.md
```

Expected: the diff only adds framework-related navigation and execution-layer links.

- [ ] **Step 6: Run diagnostics on all edited files**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/dao-tech-foundation.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 7: Commit**

```bash
git add .agents/docs/README.md .agents/docs/references/README.md .agents/docs/references/dao-tech-foundation.md
git commit -m "docs(agents): wire dao framework into navigation"
```

---

### Task 5: Final Verification And Handoff

**Files:**
- Modify: `.agents/docs/references/dao-business-mapping-framework.md`
- Modify: `.agents/docs/templates/dao-scenario-card-template.md`
- Modify: `.agents/docs/references/dao-scenario-catalog.md`
- Modify: `.agents/docs/README.md`
- Modify: `.agents/docs/references/README.md`
- Modify: `.agents/docs/references/dao-tech-foundation.md`

- [ ] **Step 1: Read all framework files together**

Run:
```bash
Get-Content .agents/docs/references/dao-business-mapping-framework.md
Get-Content .agents/docs/templates/dao-scenario-card-template.md
Get-Content .agents/docs/references/dao-scenario-catalog.md
Get-Content .agents/docs/README.md
Get-Content .agents/docs/references/README.md
Get-Content .agents/docs/references/dao-tech-foundation.md
```

Expected: the files form a coherent chain of `philosophy foundation -> framework -> template -> scenario examples -> navigation`.

- [ ] **Step 2: Scan for placeholders and ambiguous markers**

Run:
```bash
Select-String -Path .agents/docs/references/dao-business-mapping-framework.md,.agents/docs/templates/dao-scenario-card-template.md,.agents/docs/references/dao-scenario-catalog.md,.agents/docs/README.md,.agents/docs/references/README.md,.agents/docs/references/dao-tech-foundation.md -Pattern "[T]BD|[T]ODO|待补|占位|未定"
```

Expected: no matches.

- [ ] **Step 3: Run a final repository status check**

Run:
```bash
git status --short
```

Expected: only the intended framework-related doc changes are present before the final commit, or the worktree is clean if all earlier commits were made.

- [ ] **Step 4: Write the handoff summary**

Prepare this summary for the final response:
```md
**已完成**
- 新增稳定框架参考页
- 新增场景卡模板
- 新增首批示例场景库
- 打通哲学总纲、执行层框架与导航入口

**建议下一步**
- 基于 `dao-scenario-catalog.md` 选择一个场景，展开为独立 spec
- 任务完成后将结果归档到 `retrospectives/` 并回流到框架文档
```

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/references/dao-business-mapping-framework.md .agents/docs/templates/dao-scenario-card-template.md .agents/docs/references/dao-scenario-catalog.md .agents/docs/README.md .agents/docs/references/README.md .agents/docs/references/dao-tech-foundation.md
git commit -m "docs(agents): finalize dao business mapping framework assets"
```
