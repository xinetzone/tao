# 文档与产物边界规则

本文档定义 AgentForge 仓库中面向人类与 AI 的文档物理隔离原则，以及任务产物的边界约束。详细的文档治理规则（归档位置、临时产物、路径引用、同步机制等）见 [`.agents/rules/documentation.md`](documentation.md)。

## 1. 物理隔离原则

| 目录 | 面向对象 | 职责 |
|------|----------|------|
| `README.md` + `docs/` | 人类开发者 | 项目说明、技术文档、贡献指南 |
| `apps/.agents/docs/` | AI 智能体 | AI 专属知识库（参考、指南、沉淀） |
| `specs/` | 人类与 AI 公约数 | AgentForge Spec 规范文档，独立于人与 AI 各自的知识库 |

## 2. 产物边界

- 任务中间产物放入 `.temp/`，不得污染项目根目录。
- 项目内引用必须使用相对路径。
- `docs/` 采用双轨分类：`docs/tech/`（技术文档）+ `docs/general/`（通用知识），两轨严禁混入。
- `rebirth/` 中仅 `README.md` 和 `RETROSPECTIVE.md` 归 AgentForge 跟踪；其余内容通过子模块管理。

## 3. 相关规则

- 完整文档治理规则（归档、临时产物、路径引用、双向同步、真实源与镜像页等）见 [`.agents/rules/documentation.md`](documentation.md)
- 项目路径独立性规则见 [`.agents/rules/project-independence.md`](project-independence.md)
