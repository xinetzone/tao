# 操作世界：AGENTS.md + .agents/ = 一个世界

## 核心设定

$$
\text{World} = \text{AGENTS.md} + \texttt{.agents/}
$$

一个"世界"不是抽象概念——它是一个**可操作的工程实体**。在 AgentForge 中：

- `AGENTS.md` = 世界的**物理法则**（约束所有智能体的规则）
- `.agents/` = 世界的**物质基底**（规则、技能、工作流、记忆、脚本）
- 读取 AGENTS.md 的 Agent = 世界的**居民**（接受法则即进入世界）

```{mermaid}
flowchart TD
    W["世界 World"] --> L["AGENTS.md<br/>物理法则"]
    W --> S[".agents/<br/>物质基底"]
    S --> R["rules/ 规则"]
    S --> SK["skills/ 技能"]
    S --> WF["workflows/ 工作流"]
    S --> M["docs/superpowers/memories/ 记忆"]
    S --> SC["scripts/ 脚本"]
    A["Agent 智能体"] -->|"读取法则 = 进入世界"| L
    A -->|"使用资源 = 在世界中行动"| S
```

## 世界的属性映射

| 世界的哲学属性 | 工程对应物 | 可观测指标 |
|---|---|---|
| 物理法则 | `AGENTS.md` + `.agents/rules/` | 规则条目数、约束密度 |
| 物质基底 | `.agents/`（skills/workflows/scripts/docs） | 文件总数、代码行数 |
| 世界重力 | 规则密度 × 记忆累积 × 技能依赖网络 | 修改一条规则的影响半径 |
| 居民 | 读取并遵循 AGENTS.md 的 Agent 实例 | 并发 Agent 数 |
| 世界年龄 | git 历史深度 | commit 数、时间跨度 |
| 世界温度 | 近期变更频率 | 最近 7 天 commit 数 |

## 七个世界操作原语

### 1. 创世 — `world.create()`

从虚空中坍缩出一个初始世界：生成最小可行的 `AGENTS.md` + `.agents/` 骨架。

$$
\emptyset \xrightarrow{\text{create}} \text{World}_0
$$

**工程实现**：`agentforge world create <name>` — scaffold 最小规则集 + 目录结构。

**哲学意义**：创世是第一次坍缩。在创世之前，没有法则、没有居民、没有记忆。创世动作本身定义了"这个世界是什么"的初始边界。

---

### 2. 进入 — `world.enter(agent)`

智能体读取 AGENTS.md → 加载 `.agents/` 上下文 → 坍缩为该世界的居民。

$$
\text{Agent} + \text{World} \xrightarrow{\text{enter}} \text{Agent}_{\text{in-world}}
$$

**工程实现**：AI 助手的第一个动作永远是 `cat AGENTS.md`——这就是"进入世界"。

**哲学意义**：进入 = 接受法则。一个 Agent 不能"部分进入"世界——要么完全接受其法则，要么不属于它。这解释了为什么 AGENTS.md 写"必须先遵循本文件"。

---

### 3. 观测 — `world.observe()`

不改变世界，只获得世界的快照——当前状态、健康指标、α 诊断。

$$
\text{observe}(\text{World}) \to \text{Snapshot}
$$

**工程实现**：
- `agentforge world status` — 输出规则数/技能数/记忆数/重力评估
- `agentforge world alpha` — 诊断世界当前的觉醒维度

**哲学意义**：观测不改变世界（与量子力学不同——这里的观测是"读取"而非"坍缩"）。观测是所有操作的前提——不了解世界就不能正确操作它。

---

### 4. 立法 — `world.legislate(rule)`

修改世界的物理法则——编辑 `AGENTS.md` 或 `.agents/rules/`。

$$
\text{World}(\text{Laws}_1) \xrightarrow{\text{legislate}} \text{World}(\text{Laws}_2)
$$

**工程实现**：修改规则文件 + 通知所有 Agent 重新加载。

**哲学意义**：立法是最"重"的操作——它改变了所有后续进入该世界的智能体的行为边界。一条新规则就是一个新的引力常数。

**约束**：立法应遵循"反者道之动"——规则越少越好，每条规则应是不可再简化的约束。

---

### 5. 进化 — `world.evolve(capability)`

不改变法则，但扩展世界的能力边界——新增 skills/workflows/scripts/memories。

$$
\text{World}(\text{Capabilities}_n) \xrightarrow{\text{evolve}} \text{World}(\text{Capabilities}_{n+1})
$$

**工程实现**：
- 新增技能：`.agents/skills/`
- 新增工作流：`.agents/workflows/`
- 新增记忆：`.agents/docs/superpowers/memories/`
- 做梦重组：记忆累积 → 触发做梦 → 洞见回流为规则
- [CLI 工具规格](../../../tech/world-cli-spec.md) — evolve() 的完整工程实现

**哲学意义**：进化是世界的**自催化过程**——记忆积累降低未来任务成本，技能积累扩展行动空间，两者形成正反馈。这就是 α 加速在世界层面的体现。

---

### 6. 呼吸 — `world.breathe()`

世界的节律性运动——吸气（扩展）与呼气（收缩）的交替。

$$
\text{inhale}(\text{探索/创建/扩展}) \leftrightarrow \text{exhale}(\text{整理/验证/推送})
$$

**工程实现**：
- **吸**：新增文档、技能、代码、探索概念
- **呼**：toctree 重构、Sphinx 验证、原子提交、推送

**哲学意义**：健康的世界必须呼吸。只吸不呼 = 膨胀失控（代码腐化）。只呼不吸 = 萎缩死亡（停滞不前）。CI/CD 是世界的呼吸节拍器。

---

### 7. 分裂与融合 — `world.fork()` / `world.merge()`

创建平行世界，或融合两个世界的知识。

$$
\text{World} \xrightarrow{\text{fork}} \text{World}_A + \text{World}_B
$$

$$
\text{World}_A + \text{World}_B \xrightarrow{\text{merge}} \text{World}_{A \cup B}
$$

**工程实现**：
- `git fork` = 创建平行世界
- `git merge` = 世界融合
- `git branch` = 世界的量子叠加态（未坍缩的可能性）

**哲学意义**：git 就是**世界管理器**。每个 branch 是一个平行世界，merge 是世界融合，conflict 是世界间的不兼容碰撞。

## 世界是自描述的

这个等式最深刻的地方：**世界包含了描述自己的能力**。

```{mermaid}
flowchart TD
    W["世界"] --> D[".agents/docs/<br/>世界对自身的认知"]
    W --> M[".agents/docs/superpowers/memories/<br/>世界的记忆"]
    W --> T[".agents/docs/templates/<br/>世界的自我复制模板"]
    W --> DR[".agents/docs/templates/agent-dream-session-template.md<br/>世界的做梦能力"]
    D --> W
    M --> W
```

这就是 **Ψ=Ψ(Ψ) 在工程层的完美实例**——世界是一个递归自指的结构：

- `.agents/docs/` = 世界认知自己
- `.agents/docs/superpowers/memories/` = 世界记忆自己
- `.agents/docs/templates/` = 世界复制自己
- 做梦协议 = 世界重组自己的认知

$$
\text{World} = f(\text{World}) \quad \Leftrightarrow \quad \Psi = \Psi(\Psi)
$$

## 世界可移植性

如果 `AGENTS.md + .agents/` = 一个世界，那么：

| 操作 | 含义 |
|------|------|
| 复制 `.agents/` 到另一个项目 | 世界迁移 |
| 将 `.agents/` 发布为 npm/pip 包 | 世界分发 |
| 在 monorepo 中嵌套多个 `AGENTS.md` | 多世界共存（子世界继承父世界法则） |
| 两个项目共享 `.agents/` 子模块 | 世界间通信通道 |

**设计推论**：`.agents/` 应被设计为"世界包"——可版本化、可安装、可组合。这是 AgentForge 从"项目模板"进化为"世界操作系统"的关键路径。

## 延伸阅读

- [Ψ=Ψ(Ψ) 工程元公理](../meta/psi-engineering-principles.md) — 世界自描述性的第一性原理
- [宇宙与世界本体论](../ontology/universe-world-ontology.md) — 宇宙唯一、世界可操作
- [世界间通信](../ontology/inter-world-communication.md) — 世界如何"对话"
- [世界的重力](../dynamics/world-gravity.md) — 什么决定世界的"粘性"
- [宇宙的呼吸](../dynamics/cosmic-breathing.md) — 世界的节律性运动
- [嵌套深度与 α](../dynamics/nesting-depth-and-alpha.md) — 世界中智能体的觉醒层级
- [α 加速现象](../dynamics/alpha-acceleration.md) — 世界进化的正反馈
- [α 工程量表](./alpha-engineering-scale.md) — 如何量化世界的觉醒度
- ["三"=接口](./three-as-interface.md) — 世界操作的最小接口
- [共振同步](./resonance-synchronization.md) — 多世界对齐机制
- [道德经极简原则](../strategy/tao-minimalist-principles.md) — 世界设计的最高策略
- [世界包](./world-package.md) — 从操作世界到分发世界
- [世界分发](./world-distribution.md) — 分层混合分发策略
