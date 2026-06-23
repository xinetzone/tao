# 目录映射（Directory Mapping）

> 本单元涵盖原文件的 Directory Mapping、Semantic Directories Evolution 章节，将当前仓库结构映射到协作元模型，并规划语义目录的演进路径。

## Directory Mapping

第一版不新造平行体系，而是用元模型去解释现有结构。

| 当前位置 | 协作模型定位 | 说明 |
|---|---|---|
| `AGENTS.md` | `Governance Layer` 总入口 | 承载全局治理契约、任务路由与协作边界。 |
| `.agents/rules/` | `Governance Layer` 规则实现 | 承载对 `Role`、`Workflow`、知识访问等对象的约束。 |
| `.agents/workflows/` | `Execution` 域中的协作协议实例 | 承载围绕任务执行的流程化编排说明。 |
| `.agents/skills/` | `Knowledge` 域中的能力资产 | 承载可被 `Role` 或 `Agent` 使用的能力单元。 |
| `.agents/docs/` | `Knowledge` 域中的长期知识层 | 承载规则、参考、洞见、spec、复盘等知识资产。 |
| `.trae/` | `Runtime State` 的任务期工作台 | 承载 `Session`、草稿、执行中上下文与临时产物。 |

## Semantic Directories Evolution

在当前映射层稳定之后，第一批优先引入 `.agents/roles/`，并将其他语义实例目录保留为后续扩展选项，让部分核心实体拥有更直接的承载位置。

推荐候选如下：

| 候选目录 | 主要对应实体 | 建议定位 |
|---|---|---|
| `.agents/roles/` | `Role` | 职责模板、权限边界、默认规则绑定。 |
| `.agents/teams/` | `Team` | 团队边界、成员关系、默认治理策略。 |
| `.agents/agents/` | `Agent` | 执行主体画像、能力组合、角色扮演关系。 |
| `.agents/policies/` | `Policy` | 治理策略、协作限制、升级与审计规则。 |
| `.agents/workflows/` | `Workflow` | 协作协议实例，保持沿用当前目录。 |

### Recommendation for Phaseing

推荐采用“先角色、后团队、再主体”的引入顺序：

1. `.agents/roles/` 为第一批试点目录
   因为 `Role` 是 `Agent` 进入规范性协作体系的关键桥梁，也是规则、权限、技能绑定的最佳聚合点。
2. 再考虑 `.agents/teams/`
   因为 `Team` 更偏治理边界与组织容器，应建立在 `Role` 的稳定语义之上。
3. 最后考虑 `.agents/agents/`
   因为 `Agent` 最容易与具体实现、模型厂商或运行时形态耦合，适合在前两者稳定后再落目录。

### Guardrails

- 这些目录属于协作模型的“实例层承载”，不是元模型定义本身
- 第一版即使只创建 `.agents/roles/`，元模型依然成立
- 一旦引入，目录内文件应优先保存声明式语义，而不是执行日志或临时上下文
- `roles/` 应优先承载职责模板和约束绑定，不应退化为杂项提示词仓库
- `agents/` 不应直接等同于某个模型提供商配置集合
