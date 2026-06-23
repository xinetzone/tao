---
paths:
  - ".agents/rules/**"
  - "docs/topics/**"
---

# 规则演化与生长通道

本文档定义经验上升为规则的准入标准（生长通道）以及规则自身的演化机制（元规则），用于约束 `.agents/rules/` 与 `docs/topics/` 之间的双向流动。

## 1. 生长通道准入标准

并非所有经验都应固化为规则。一条经验只有同时通过**五维准入检验**，才允许进入 `.agents/rules/`。

### 1.1 五维准入检验

| 维度 | 问题 | 判定标准 | 反例 |
|------|------|---------|------|
| 频率 | 是否反复出现？ | **≥ 3 次独立触发** | 仅偶然遇到一次 |
| 普适性 | 跨人 / 跨场景是否仍有效？ | **不依赖特定个体偏好** | "我习惯把 import 写两行" |
| 可执行性 | 能否写成明确约束？ | **MUST / MUST NOT / SHOULD 句式** | "代码要写得优雅" |
| 无害性 | 是否阻碍创新？ | **只约束已知反模式，不预设解法** | "所有对象必须用工厂模式" |
| 可验证性 | 违反时能否检测？ | **CI / review / 自动化脚本可查** | "要有全局视野" |

> 五维**全部满足**方可进入候选；缺一即应停留在 `docs/topics/` 经验层。

### 1.2 操作流程

```mermaid
flowchart LR
    E["经验出现"] --> R["记录<br/>retrospective"]
    R --> M["标记候选<br/>docs/topics/"]
    M --> D["提炼草案<br/>rule draft"]
    D --> C["共识评审<br/>PR 讨论"]
    C --> F["固化<br/>.agents/rules/"]
    C -. 未通过 .-> M
```

| 阶段 | 产物位置 | 退出条件 |
|------|---------|---------|
| 记录 | `.temp/` 或 retrospective | 触发次数累积 ≥ 3 |
| 标记 | `docs/topics/` | 五维检验初判通过 |
| 提炼 | PR 中的草案文件 | 句式可机读，路径范围清晰 |
| 共识 | PR review | 至少一名核心维护者批准 |
| 固化 | `.agents/rules/*.md` | 含 frontmatter `paths` 与交叉引用 |

### 1.3 反模式（不应上升为规则）

- **个人风格偏好**：缩进、命名喜好等无客观对错的项。
- **一次性救火经验**：仅适用于某次事故的 workaround。
- **预设解法**：强制使用某种设计模式或库，而非约束反模式。
- **无法检测的口号**：如"保持优雅""注意性能"。
- **绑定具体人 / 时间**：如"X 离职前的临时约定"。

## 2. 元规则：规则如何演化

### 2.1 三条元规则

| 元规则 | 内容 | 哲学依据 |
|--------|------|---------|
| **慢变原则** | 宇宙层（Kernel）规则变更周期 **≥ 10x** 世界层迭代周期 | 治大国若烹小鲜 |
| **替代原则** | **不可简单删除**，只能用更好的规则替代或显式标记 deprecated | 有生于无 |
| **溯源原则** | 每条规则必须**可追溯到具体世界层教训**（链接 retrospective / topic） | 道法自然 |

### 2.2 规则生命周期

```mermaid
stateDiagram-v2
    [*] --> Candidate: 五维检验通过
    Candidate --> Active: PR 共识合入
    Active --> Challenged: 出现合理违反
    Challenged --> Refined: 缩窄 / 泛化 / 分裂
    Challenged --> Deprecated: 被更好规则替代
    Refined --> Active
    Deprecated --> [*]
```

### 2.3 演化触发条件

进入 `Challenged` 状态并启动演化，需**同时满足**：

- 规则与现实持续冲突，**合理违反 ≥ 5 次**。
- 社区 / 团队形成共识，**非单人决策**。
- 存在**明确的替代方案**或更精细的边界划分。

### 2.4 演化方式

| 方式 | 含义 | 典型场景 |
|------|------|---------|
| **缩窄** | 通过 `paths` 或前置条件收紧适用范围 | 规则在边缘场景产生噪声 |
| **泛化** | 抽象出更上位的约束，覆盖多条同源规则 | 多条规则重复表达同一意图 |
| **废弃** | 标记 `deprecated` 并指向替代规则，**保留链接** | 被新规则完全包含 |
| **分裂** | 拆分为多条带条件的子规则 | 单一规则承载了互斥意图 |

### 2.5 规则使用反馈闭环

规则固化后,需要持续收集 Agent 实际使用信号,形成"使用 → 反馈 → 改进"闭环。规则文件的 `usage_feedback` frontmatter 字段承载这一信号,作为 `Challenged` 状态判定的数据依据。

#### 2.5.1 字段定义

完整字段说明见 [`docs/templates/rule-frontmatter-template.md`](../docs/templates/rule-frontmatter-template.md)。核心字段:

| 字段 | 作用 | 维护方 |
|------|------|--------|
| `total_invocations` | 规则被引用总次数 | Agent 自动累加 |
| `success_count` / `failure_count` | 应用后任务成功 / 失败次数 | Agent 自动累加 |
| `last_invoked` | 最后一次引用日期 | Agent 自动更新 |
| `failure_reasons` | 失败原因明细(含 workaround) | Agent 记录 |
| `agent_notes` | 规则缺口或过时内容标注 | Agent 主动标注 |

#### 2.5.2 Agent 更新时机

Agent 在以下场景必须更新所引用规则的 `usage_feedback` 字段:

| 场景 | 更新动作 |
|------|----------|
| 引用规则后任务成功 | `total_invocations` +1,`success_count` +1,`last_invoked` 设为今日 |
| 引用规则后任务失败 | `total_invocations` +1,`failure_count` +1,`last_invoked` 设为今日,追加 `failure_reasons` 条目 |
| 发现规则缺口或过时内容 | 追加 `agent_notes` 条目(含 timestamp、agent、note) |
| 发现既有 `failure_reasons` 的 workaround | 更新对应条目的 `workaround` 字段 |

#### 2.5.3 更新原则

- **数据必须来自 Agent 实际使用**,禁止人工编造(编造数据会误导规则演化决策)。
- **`failure_reasons` 比 `success_count` 更有价值**——失败信号驱动改进,成功信号只用于统计。
- **`agent_notes` 是规则演化的种子**——累积到一定数量后,应触发 §2.3 的 `Challenged` 状态判定。
- **`agent_notes` 应定期归档**——超过 3 个月的 notes 应迁移到 retrospective,避免 frontmatter 无限膨胀。

#### 2.5.4 反馈数据与演化触发的关系

`usage_feedback` 数据为 §2.3 的演化触发条件提供量化依据:

```mermaid
flowchart LR
    A["Agent 使用规则"] --> B["更新 usage_feedback"]
    B --> C{"failure_count / total ≥ 20%?"}
    C -->|否| D["维持 Active"]
    C -->|是| E["进入 Challenged 候选"]
    E --> F{"agent_notes ≥ 3 条<br/>指向同一缺口?"}
    F -->|是| G["启动演化<br/>缩窄/泛化/分裂"]
    F -->|否| H["继续观察"]
```

#### 2.5.5 试点范围

当前试点规则:`python.md`。试点稳定后,逐步推广到 `documentation.md`、`context-economy.md` 等高频规则。推广顺序见 [`docs/templates/rule-frontmatter-template.md`](../docs/templates/rule-frontmatter-template.md) 的 Adoption Roadmap 章节。

## 3. 哲学映射

> **为学日益，为道日损。**

- **为学日益**：经验在 `docs/topics/` 持续累积，对应生长通道的"加法"。
- **为道日损**：规则在 `.agents/rules/` 通过演化不断收敛精炼，对应元规则的"减法"。

加减之间，规则系统保持自指稳定（Ψ=Ψ(Ψ)）：经验喂养规则，规则反哺经验筛选。

## 参见

- [`world-hierarchy.md`](world-hierarchy.md)
- [`core-principles.md`](core-principles.md)
- [`../../../../docs/topics/code-architecture-insights.md`](../../../../docs/topics/code-architecture-insights.md)
