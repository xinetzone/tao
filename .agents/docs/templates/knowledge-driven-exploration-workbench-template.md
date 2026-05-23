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
