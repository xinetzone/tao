# 新角色提案模板

使用本模板向 `.agents/roles/` 提交新角色提案。提案文件命名为 `<role-name>-proposal.md`，放入 `.agents/roles/proposals/`。

---

# [角色名称] 提案

## Role Identity

- **Name**: `[英文小写连字符，如 knowledge-curator]`
- **Domain**: [Organization / Execution / Knowledge / Governance]
- **Description**: [一句话说明角色定位与核心价值]

## Motivation

[为什么需要这个角色？当前协作体系中存在什么空白或痛点？]

## Responsibilities

- [核心职责 1 — 使用"设计/维护/审核/规范/评估"等编排性动词，避免"执行/实现/调用"等运行时动词]
- [核心职责 2]
- [核心职责 3]

## Default Bindings

### Rules

- [`.agents/rules/xxx.md` — 必须真实存在于仓库]

### References

- [`.agents/docs/references/xxx.md` — 必须真实存在于仓库]

### Skills

- [skill-name — 必须存在于 `.agents/skills/`]

## Non-Goals

- [明确排除项 1 — 至少一条排除运行时实现]
- [明确排除项 2]

## Impact Assessment

[该角色引入后对现有角色、目录映射、工作流、规则体系的潜在影响。如果无影响，说明原因。]

---

## 提交检查清单

提交前逐项确认：

- [ ] Name 使用英文小写连字符，不与现有角色名重复
- [ ] Domain 属于五大领域之一
- [ ] Default Bindings 中所有引用路径真实存在
- [ ] Responsibilities 使用编排性动词，不描述具体执行细节
- [ ] Non-Goals 至少有一条排除运行时实现
- [ ] Impact Assessment 已填写
