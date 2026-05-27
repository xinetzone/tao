# 新 Team 提案模板

使用本模板向 `.agents/teams/` 提交新 Team 提案。提案文件命名为 `<team-name>-proposal.md`，放入 `.agents/teams/proposals/`。

---

# [Team 名称] 提案

## Team Identity

- **Name**: `[英文小写连字符，如 delivery-team]`
- **Domain**: Organization
- **Description**: [一句话说明 Team 的治理边界与核心价值]

## Motivation

[为什么需要这个 Team？当前治理结构中存在什么空白或痛点？]

## Responsibilities

- [核心职责 1 — 聚焦治理与边界维护，避免运行时执行]
- [核心职责 2]
- [核心职责 3]

## Member Roles

| Role | 绑定原因 |
|---|---|
| `[role-name]` | [该角色在此 Team 中的治理价值] |

## Cross-Team Policy

[当前单 Team 模式下声明"欢迎后续引入子团队"；多 Team 模式下描述跨 Team 协作的 Handoff 协议与治理边界]

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

[该 Team 引入后对现有角色、目录映射、工作流、规则体系的潜在影响。如果无影响，说明原因。]

---

## 提交检查清单

提交前逐项确认：

- [ ] Name 使用英文小写连字符，不与现有 Team 名重复
- [ ] Domain 固定为 Organization
- [ ] Member Roles 中所有 Role 真实存在于 `.agents/roles/`
- [ ] Default Bindings 中所有引用路径真实存在
- [ ] Cross-Team Policy 已声明
- [ ] Non-Goals 至少有一条排除运行时实现
- [ ] Impact Assessment 已填写
