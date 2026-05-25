# Memories: 长期记忆条目

本目录存储从复盘报告中提取的、已验证可复用的长期知识条目。

## 定位

- **memories/** 关注"为什么这样做" — 记录决策依据、经验教训、约束边界
- **references/** 关注"怎样使用" — 快速参考、命令、配置

## 命名规范

```
YYYY-MM-DD-<记忆主题>-<类型>.md
```

示例：
- `2026-05-25-doc-maintenance-5-steps-experience.md`
- `2026-05-25-myst-cross-directory-link-constraint.md`

类型后缀（可选）：`experience` / `constraint` / `principle` / `fact`

## 入选条件（Gate Rules）

一条信息进入本目录前，必须满足：

- [ ] 已相对稳定（非当前任务进度、非未验证猜测）
- [ ] 未来可复用（至少适用于 2+ 类场景）
- [ ] 能降低成本（理解/决策/排查成本）
- [ ] 有明确适用范围
- [ ] 有明确过期条件
- [ ] 已有来源标注
- [ ] 建议了回流位置

不应进入本目录的内容：
- 当前任务进度（应留在 `.temp/`）
- 一次性命令输出（应归档到 `retrospectives/`）
- 未验证的假说（应标记为候选）

## 模板

所有条目按 [`../../templates/agent-memory-entry-template.md`](../../templates/agent-memory-entry-template.md) 格式编写。

## 生命周期

```
复盘报告 → 提取记忆候选 → 按模板编写 → 累积多条 → 触发做梦 → 回流至 rules/references
```

详见 [`../../references/agent-memory-dream-protocol.md`](../../references/agent-memory-dream-protocol.md)。
