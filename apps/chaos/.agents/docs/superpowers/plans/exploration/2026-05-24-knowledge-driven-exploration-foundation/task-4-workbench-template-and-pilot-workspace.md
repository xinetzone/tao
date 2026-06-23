# Task 4: Create The Workbench Template And The First Pilot Workspace

**Files:**
- Create: `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md`
- Create: `.trae/specs/exploration-knowledge-loop-pilot/spec.md`
- Create: `.trae/specs/exploration-knowledge-loop-pilot/tasks.md`
- Create: `.trae/specs/exploration-knowledge-loop-pilot/checklist.md`

- [ ] **Step 1: Inspect the current `.trae/specs/` file pattern**

Run:
```bash
Get-ChildItem .trae/specs
Get-Content .trae/specs/adopt-mise-dev-environment/spec.md
Get-Content .trae/specs/adopt-mise-dev-environment/tasks.md
Get-Content .trae/specs/adopt-mise-dev-environment/checklist.md
```

Expected: each workspace uses the three-file structure `spec.md`、`tasks.md` and `checklist.md`.

- [ ] **Step 2: Create the workbench template page**

Create `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md` with exactly:
```md
# Knowledge-Driven Exploration Workbench Template

## Usage

用于在 `.trae/specs/<topic>/` 下创建执行中的探索工作台，保持 spec、tasks 与 checklist 三个文件结构稳定。

## Directory Layout

```text
.trae/specs/<topic>/
├── spec.md
├── tasks.md
└── checklist.md
```

## spec.md Skeleton

```md
# Spec

## Goal

- 本次试点要验证什么

## Scope

- 本次会做什么

## Non-Goals

- 本次明确不做什么

## Deliverables

- 具体产物

## Risks

- 当前主要风险
```

## tasks.md Skeleton

```md
# Tasks
- [ ] Task 1: 补齐场景卡与 spec。
- [ ] Task 2: 生成实施计划。
- [ ] Task 3: 完成最小验证。
- [ ] Task 4: 输出复盘并回流。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
```

## checklist.md Skeleton

```md
- [ ] 场景卡已完成并字段完整
- [ ] spec 已完成并边界清晰
- [ ] plan 已完成并可执行
- [ ] 至少完成一次最小验证
- [ ] 已输出复盘并指定回流动作
```
```

- [ ] **Step 3: Create the pilot spec**

Create `.trae/specs/exploration-knowledge-loop-pilot/spec.md` with exactly:
```md
# Spec

## Goal

- 以最小成本验证“场景卡 -> spec -> plan -> 验证 -> 复盘 -> 回流”是否可以在 AgentForge 中稳定跑通。

## Scope

- 使用统一探索协议页作为规则入口
- 使用场景卡模板组织试点场景
- 使用计划文档驱动实施顺序
- 以一次真实复盘验证回流路径

## Non-Goals

- 本次不实现新的自动化工作流
- 本次不构建 UI 或数据库
- 本次不同时展开多个独立探索主题

## Deliverables

- 一个协议页
- 一组模板资产
- 一个 `.trae` 试点工作台
- 一份复盘回流动作

## Risks

- 试点范围可能因为文档膨胀而失控
- 回流动作如果不明确，试点会退化为一次性记录
```

- [ ] **Step 4: Create the pilot task list**

Create `.trae/specs/exploration-knowledge-loop-pilot/tasks.md` with exactly:
```md
# Tasks
- [ ] Task 1: 完成协议页与模板资产。
- [ ] Task 2: 将试点场景写入长期场景目录。
- [ ] Task 3: 更新导航入口并验证引用链路。
- [ ] Task 4: 输出复盘并确认至少一个回流动作。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
- [Task 4] depends on [Task 1, Task 2, Task 3]
```

- [ ] **Step 5: Create the pilot checklist**

Create `.trae/specs/exploration-knowledge-loop-pilot/checklist.md` with exactly:
```md
- [ ] 已创建统一探索协议页
- [ ] 已升级场景卡模板并包含三类适配视图
- [ ] 已创建 spec、retrospective 与 workbench 模板
- [ ] 已创建 `.trae/specs/exploration-knowledge-loop-pilot/` 工作台
- [ ] 已将试点场景写入长期场景目录
- [ ] 已更新 AI 文档导航入口
- [ ] 已完成一次复盘并指定回流动作
```

- [ ] **Step 6: Verify the new template and pilot workspace**

Run:
```bash
Get-Content .agents/docs/templates/knowledge-driven-exploration-workbench-template.md
Get-Content .trae/specs/exploration-knowledge-loop-pilot/spec.md
Get-Content .trae/specs/exploration-knowledge-loop-pilot/tasks.md
Get-Content .trae/specs/exploration-knowledge-loop-pilot/checklist.md
```

Expected: the template explains the `.trae/specs/<topic>/` directory shape, and the pilot files use a coherent `spec / tasks / checklist` trio.

- [ ] **Step 7: Commit**

```bash
git add .agents/docs/templates/knowledge-driven-exploration-workbench-template.md .trae/specs/exploration-knowledge-loop-pilot/spec.md .trae/specs/exploration-knowledge-loop-pilot/tasks.md .trae/specs/exploration-knowledge-loop-pilot/checklist.md
git commit -m "docs(exploration): add workbench template and pilot workspace"
```
