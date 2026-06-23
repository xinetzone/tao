# 脱胎萃取规则

本文档定义双态架构（混沌/脱胎）下"萃取"与"重命名"的边界，约束从混沌态向脱胎态迁移资产时的行为。处理脱胎、萃取、包名迁移、混沌态与脱胎态边界相关任务时，应先读取本文档。

## 1. 核心规则

### 1.1 萃取 ≠ 重命名

- **MUST**：脱胎态（`rebirth/`）的资产（包名、模块、文档）必须**独立创建**，从混沌态（`apps/chaos/`）萃取稳定功能后重新实现。
- **MUST NOT**：禁止将混沌态的资产"全项目重命名"为脱胎态名称——这混淆了双态架构的职责边界。
- **MUST**：混沌态的包名、个人色彩、哲学内核保留不变——保留个人色彩是混沌态的设计意图，不是缺陷。
- **MUST NOT**：禁止要求混沌态承担脱胎态的"去个人化"义务——去个人化是脱胎过程，不是混沌态的义务。

### 1.2 萃取流程

```mermaid
flowchart LR
    A["混沌态资产<br/>（个人色彩、实验代码）"] --> B["萃取<br/>（去个人化/去哲学化）"]
    B --> C["脱胎态资产<br/>（社区标准、独立创建）"]
    C --> D["git push<br/>（独立仓库）"]
```

- **MUST**：萃取时从混沌态选取稳定功能，在脱胎态中**重新实现**（非复制粘贴式搬迁）。
- **MUST**：私有基础设施（如 `src/taolib/github_app/`）不迁移——在脱胎态中排除或独立重新设计。
- **SHOULD**：萃取后的脱胎态资产应有独立的包名、独立的 PyPI 发布、独立的文档站点。

## 2. 反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 全项目重命名（如 taolib→sproutlib） | 混淆双态边界；~100 文件 227+ 引用的高成本高风险操作；影响 PyPI/ReadTheDocs 现有用户 | `rebirth/worldsprout/` 独立创建 sproutlib 包，从 taolib 萃取稳定功能 |
| 要求混沌态去个人化 | 违反双态设计意图；混沌态的哲学内核是设计的一部分 | 混沌态保留个人色彩；脱胎态通过萃取去个人化 |
| 复制粘贴式搬迁 | 脱胎态继承了混沌态的技术债和个人化内容 | 萃取时重新实现，天然完成去个人化 |

## 3. 验证方式

- **CI 检查**：脱胎态仓库（`rebirth/worldsprout/`）的包名必须与混沌态（`apps/chaos/`）不同。
- **Review 检查**：涉及脱胎/萃取的 PR 必须引用本规则，确认遵循"独立创建"而非"重命名"。
- **自动化脚本**：可通过脚本检查混沌态包名是否被错误地要求重命名。

## 4. 来源与状态

- **来源**：[`../docs/superpowers/retrospectives/retrospective-agentforge-comprehensive-20260623.md`](../docs/superpowers/retrospectives/retrospective-agentforge-comprehensive-20260623.md) 附录 A.6
- **状态**：Draft（草案）——五维评估中频率维度目前仅 1 次触发，待累积至 ≥ 3 次后转为 Active
- **五维评估**：

| 维度 | 状态 | 说明 |
|------|------|------|
| 频率 | ⚠️ 1/3 | 待累积；首次触发于 taolib→sproutlib 决策重新评估 |
| 普适性 | ✅ | 不依赖特定个体偏好；适用于所有双态架构下的资产迁移 |
| 可执行性 | ✅ | MUST / MUST NOT 句式，路径范围清晰 |
| 无害性 | ✅ | 只约束"全项目重命名"反模式，不预设具体解法 |
| 可验证性 | ✅ | CI 可检查包名差异；review 可检查 PR 引用 |

## 5. 哲学映射

> **反者道之动，弱者道之用。**

- **反者道之动**：脱胎态是混沌态的"反"——去个人化、去哲学化，但两者并非对立，而是循环（混沌→萃取→脱胎→反馈→混沌）。
- **弱者道之用**：混沌态保留"弱"（个人色彩、实验性），正是其能自由生长的根源；脱胎态追求"强"（社区标准、稳定性），但需通过萃取而非强制重命名来达成。

## 参见

- [`world-hierarchy.md`](world-hierarchy.md) — 多世界继承与覆盖
- [`rule-evolution.md`](rule-evolution.md) — 规则准入标准与生命周期
- [`../../../../rebirth/RETROSPECTIVE.md`](../../../../rebirth/RETROSPECTIVE.md) — 脱胎复盘
- [`../docs/superpowers/retrospectives/retrospective-agentforge-comprehensive-20260623.md`](../docs/superpowers/retrospectives/retrospective-agentforge-comprehensive-20260623.md) — 综合复盘附录 A
