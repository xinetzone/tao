# Memories: 长期记忆条目

> **维护责任人**：Leader Agent
> **模块化日期**：2026-06-23

本目录存储从复盘报告中提取的、已验证可复用的长期知识条目。经模块化重构后，记忆条目按类型分为 **principles/、experiences/、constraints/、methodologies/** 四个模块。

## 定位

- **memories/** 关注"为什么这样做" — 记录决策依据、经验教训、约束边界
- **references/** 关注"怎样使用" — 快速参考、命令、配置

## 模块导航

| 模块 | 类型 | 文件数 | 说明 | 入口 |
|------|------|--------|------|------|
| `principles/` | 原则 | 4 | 记录项目设计、知识构建、外部知识入库的通用原则 | [README](./principles/README.md) |
| `experiences/` | 经验 | 2 | 记录文档维护、知识图谱构建的实战经验 | [README](./experiences/README.md) |
| `constraints/` | 约束 | 1 | 记录 MyST 跨目录链接等技术约束 | [README](./constraints/README.md) |
| `methodologies/` | 方法论 | 1 | 记录文档债务治理等可复用方法论 | [README](./methodologies/README.md) |

## 命名规范

```
YYYY-MM-DD-<记忆主题>-<类型>.md
```

示例：
- `2026-05-25-doc-maintenance-5-steps-experience.md`
- `2026-05-25-myst-cross-directory-link-constraint.md`

类型后缀：`experience` / `constraint` / `principle` / `methodology` / `fact`

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

## 元数据文档

| 文档 | 用途 |
|------|------|
| [`_meta/naming-convention.md`](./_meta/naming-convention.md) | 命名规范 |
| [`_meta/module-catalog.md`](./_meta/module-catalog.md) | 模块目录清单 |
| [`_meta/dependency-graph.md`](./_meta/dependency-graph.md) | 依赖关系图谱 |
| [`_meta/migration-log.md`](./_meta/migration-log.md) | 迁移日志 |

## 检索指南

| 需求 | 去向 |
|------|------|
| 查找设计原则、通用规则 | `principles/` |
| 查找实战经验、最佳实践 | `experiences/` |
| 查找技术约束、边界条件 | `constraints/` |
| 查找可复用方法论、流程 | `methodologies/` |
| 了解模块间引用关系 | `_meta/dependency-graph.md` |
| 查看迁移完整性 | `_meta/migration-log.md` |
