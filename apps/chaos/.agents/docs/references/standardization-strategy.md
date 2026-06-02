# AgentForge 标准化战略：从挑战分析到三层分离方案

> 本文档整合了标准化战略分析（三大挑战、超集兼容策略、战略优势）与正交三层分离方案（Layer 1/2/3、Phase 路径），形成完整的战略叙事：**问题 → 定位 → 方案 → 路线图**。

---

# 上篇：问题分析与战略定位

## 一、行业格局：谁在定义"AI Agent 项目约定"

当前 AI Agent 项目约定领域已形成三大流派：

| 维度 | **AGENTS.md 标准** (开放标准) | **CLAUDE.md + .claude/** (Anthropic) | **AGENTS.md + .agents/** (AgentForge) |
|------|------|------|------|
| 定位 | "AI 的 README" | "Claude Code 的项目配置" | "AI 智能体的世界" |
| 入口文件 | AGENTS.md（扁平 Markdown） | CLAUDE.md（路由文件，< 200 行） | AGENTS.md（路由契约 + Mermaid） |
| 目录 | 无约定 | `.claude/` | `.agents/` |
| 规则 | 全部写入口文件 | `.claude/rules/` + `paths:` frontmatter | `.agents/rules/` + 任务路由表 |
| 技能 | 不涉及 | `.claude/skills/` + SKILL.md + 捆绑文件 | `.agents/skills/` + SKILL.md + 评测 |
| 子智能体 | 不涉及 | `.claude/agents/` + 工具白名单 | `.agents/roles/` + `.agents/teams/` + 协作元模型 |
| 声明式配置 | 无 | `settings.json`（权限/hooks） | `world.toml`（kernel/fragments/capabilities/memory） |
| 条件加载 | 嵌套 AGENTS.md 就近优先 | `paths:` frontmatter glob 匹配 | 任务类型 → 规范入口路由表 |
| 记忆 | 不涉及 | `agent-memory/`（自动写入 MEMORY.md） | `docs/superpowers/memories/`（模板提取 + 做梦协议） |
| 哲学 | 无 | 无 | Ψ=Ψ(Ψ) + 道德经驱动 |
| 支持方 | OpenAI/Google/Cursor/30+ 工具 | 仅 Claude Code | 自研 |

**关键事实**：AGENTS.md 已被 Linux 基金会下的 Agentic AI Foundation 托管，GitHub 上 60k+ 仓库采用，30+ 工具通用读取。AgentForge 在同一个名字下装了远超 Codex 预期的内容——`AGENTS.md` 的名字已被 OpenAI Codex 占用，但 Codex 只把它当作一个简单指令文件。

---

## 二、核心挑战

### 挑战 1：复杂度梯度问题

一个标准要流行，必须满足**5 分钟上手法则**：

- **Codex 的 AGENTS.md**：一个 Markdown 文件，写几行指令就能用 → 5 秒上手
- **AgentForge 的体系**：需要理解 world.toml / kernel / fragments / capabilities / memory / 世界继承 / 不可变法则 / 上下文路由 / 角色模型 / 团队协作……

如果一个开发者只想"让我的 AI 助手知道项目用 TypeScript + pnpm"，他需要穿越整个哲学体系才能开始。

**需要一个渐进式复杂度模型**——每一层必须向下兼容且独立可用：

```
Level 0:  AGENTS.md（单文件，兼容 Codex 格式）     ← 90% 的用户停在这里
Level 1:  AGENTS.md + .agents/rules/（按领域拆规则）  ← 中型项目
Level 2:  + .agents/skills/ + workflows/             ← 技能生态用户
Level 3:  + world.toml + kernel/fragments            ← 治理级项目
Level 4:  + 多世界继承 + roles/teams                  ← 多团队协作
```

### 挑战 2：与现有事实标准的关系

三种可选策略：

| 策略 | 做法 | 风险 |
|------|------|------|
| **竞争替代** | 推出独立的 "AgentForge Standard" | 需对抗 Codex/Cursor/Claude 三个生态的惯性 |
| **超集兼容** | AGENTS.md 保持 Codex 兼容，.agents/ 作为增强层 | 最务实，但容易被视为"Codex 的一个方言" |
| **协议抽象** | 把核心协议抽成独立规范（不绑定 AGENTS.md 名字） | 最干净，但放弃已有的名称认知 |

**推荐策略 2：超集兼容**——`AGENTS.md` 前 N 行必须是纯 Markdown 指令（兼容 Codex），`.agents/` 作为可选增强协议，`world.toml` 作为高级治理协议。

### 挑战 3：规范 vs 实现分离

当前规范和实现耦合在同一个项目里。要成为标准，需要三件分离的事物：

1. **独立的规范仓库**（只放协议定义、Schema、示例）
2. **独立的参考实现**（当前 `apps/chaos/` 是之一）
3. **独立的验证工具**（类似 JSON Schema Validator）

类比：JSON（规范） vs `json` 库（实现） vs JSON Schema（验证）。

### 挑战 4（补充）：核心定位矛盾

AgentForge 有一个**定位错位**：

> 战略目标是"通用标准"，但设计出发点是"世界"。

"世界"意味着完整性——一切都在世界之内，哲学内核是不可分割的 kernel。而"标准"意味着可选性——别人只采用他们需要的部分，其余部分应该可以不装。

当前 `world.toml` 里 `psi-philosophy` 标记了 `optional = false`——哲学内核对本世界不可选，但对**标准**应该可选。你的设计是从"世界"自上而下构建的，但标准的采用是从"项目"自下而上生长的。要成为通用标准，需要一个不需要接受哲学内核就能采用的子集。

---

## 三、战略优势与核心洞见

### 已有的战略优势

#### 1. 技能层已对齐 agentskills.io

`SKILL.md` 已与 agentskills.io 开放标准高度兼容，在技能层不需要"重新发明轮子"，可直接复用生态。

#### 2. 世界层级继承是独家能力

当前没有任何竞品定义了**多 AGENTS.md 继承 + kernel 不可变 + 覆盖粒度控制**：

```
root/AGENTS.md          ← 公司级规则（代码风格、安全策略）
├── frontend/AGENTS.md  ← 前端团队覆盖（React 规范）
├── backend/AGENTS.md   ← 后端团队覆盖（Go 规范）
└── shared/AGENTS.md    ← 共享库规则
```

这是 Codex/Cursor/Claude **完全没有解决的问题**。

#### 3. kernel/fragments 分层是独创性贡献

把项目约定分为"不可变内核"和"可插拔能力片段"，在 AI Agent 约定领域是全新的。对于开源项目尤其有价值——维护者可以声明"这些规则不可被子项目覆盖"。

### 关键洞见

#### 洞见一：`.agents/` 正在解决一个 AGENTS.md 标准刻意回避的问题

AGENTS.md 标准的哲学是"Just Markdown, no prescribed structure"——它只定义入口文件，不定义目录约定。这是刻意的：降低采用门槛。但这留下了一个真空：**AI Agent 项目的结构化资产怎么组织？**

`.agents/` 正是在回答这个问题——`world.toml` 把答案形式化了（kernel → fragments → capabilities → memory）。如果项目战略定位是"通用标准"，`.agents/` 目录约定本身就应该是标准化的输出物。

#### 洞见二：`world.toml` 是最被低估的设计

`world.toml` 做了一件别人都没做的事——**声明式地定义了一个世界的构成法则和可移植边界**。`portable = true/false` 直接回答了"什么可以跨项目复用、什么是项目特有"；`immutable_rules` 定义了"子世界不能覆盖的宇宙法则"——这是 OpenAI 88 个 AGENTS.md 靠"就近优先"没有解决的声明机制。

#### 洞见三：协作元模型是"概念的先锋，工程的孤岛"

AgentForge 的角色体系设计用心，但对比 Claude Code 的 `.claude/agents/`，后者有 `tools:` 字段实现运行时强制约束。AgentForge 的 Default Bindings 是**指导性声明**而非运行时约束。如果目标是通用标准，需要回答——**谁来执行这些声明？** 如果答案是"靠 AI 自觉遵守"，标准就是文档而不是协议。

#### 洞见四：技能体系是最容易输出标准的部分

SKILL.md 和 Claude Code skills 几乎同构。AgentForge 在**评测**和**分发**上领先（`.validate-config.toml`、`registry.toml`），但在**动态参数**和**调用控制**上落后。技能体系不依赖 Ψ=Ψ(Ψ) 哲学内核、不依赖 world.toml，是纯工程约定——最容易脱钩输出标准。

#### 洞见五：最大的结构性机会——从"AI 的世界"到"AI 可读的项目协议"

> AGENTS.md 标准 = AI 的 README（解决了入口问题）
> `.agents/` = AI 可读的项目操作系统（解决结构化资产问题）

要让后者成为通用标准，需要做一次**关注点分离**：

```
哲学内核层（Ψ=Ψ(Ψ)、道德经）    ← AgentForge 特色，保留为 fragment
─────────────────────────────
通用协议层（目录约定、world.toml schema、
  SKILL.md 规范、角色声明格式）  ← 可以标准化的部分
─────────────────────────────
执行层（glob 条件加载、工具权限、
  hooks、自动记忆）              ← 需要补齐的部分
```

当前三层是混在一起的——`world.toml` 里 `psi-philosophy` 标记 `optional = false`，哲学内核对本世界不可选，但对**标准**应该可选。

---

# 下篇：解决方案与路线图

## 四、正交三层分离方案

Spec v0.1 的 Level 0-4 渐进式采纳模型解决的是**功能增量**问题（从最简单到最复杂），不是**关注点分离**问题（从通用到特定）。需要的是**正交的分层**：

```
┌─────────────────────────────────────────────┐
│  Layer 3: World Runtime（世界运行时）        │
│  哲学内核、做梦协议、认知循环、宇宙法则       │
│  → AgentForge 特有，不可移植                 │
├─────────────────────────────────────────────┤
│  Layer 2: Collaboration Metamodel（协作协议） │
│  Team/Role/Agent 语义、Handoff 约定、        │
│  目录映射规则、强约束/弱约束分层              │
│  → 可标准化，但需要 AOI 实现才生效           │
├─────────────────────────────────────────────┤
│  Layer 1: Project Protocol（项目协议）        │
│  AGENTS.md 路由格式、.agents/ 目录约定、      │
│  world.toml 基础 schema、SKILL.md 规范       │
│  → 任何项目零前提采用                        │
└─────────────────────────────────────────────┘
```

**关键**：三层是**正交的**——一个项目可以只采用 Layer 1 而不知道 Layer 2/3 的存在。这和 Level 0-4 渐进式模型不矛盾，而是另一个维度。

---

### Layer 1：项目协议——标准化的最小公约数

Layer 1 回答的问题是：**一个项目只想要"AI 能读懂我的项目结构"，最小需要什么？**

| Layer 1 组件 | 当前状态 | 需要脱钩的 |
|---|---|---|
| AGENTS.md 路由格式 | 已有，但包含"哲学驱动"等世界级约束 | 路由表格式独立于世界契约 |
| `.agents/` 目录约定 | 已有 | `kernel/` 目录不应是 Layer 1 必需 |
| `world.toml` 基础 schema | 已有，但 kernel 包含哲学引用 | Layer 1 的 world.toml 只需 `[world]` + `[fragments]` |
| SKILL.md 规范 | 已有 | 不依赖 world.toml 即可独立使用 |
| 条件加载 | 路由表方式 | 应叠加 glob frontmatter |

Layer 1 的 `world.toml` 最小 schema：

```toml
[world]
name = "my-project"
version = "1.0.0"

[fragments.python-engineering]
includes = ["rules/python.md"]
optional = true
```

没有 `[kernel]`，没有 `immutable_rules`，没有 `min-alpha`——这些是 Layer 2/3 的概念。

---

### Layer 2：协作协议——元模型的标准化

AgentForge 的协作元模型定义了 15 个核心实体和双层结构，比任何主流工具都超前。但要让 Layer 2 成为标准，需要从**描述性**变成**操作性**：

```markdown
# 当前：描述性声明
- Agent 必须通过 Role 进入规范性协作体系
- Handoff 必须是显式对象
```

```toml
# 需要变成：操作性协议（constraints.toml）
[constraints.strong]
agent_requires_role = true
handoff_explicit = true
task_must_belong_to_mission = true

[constraints.weak]
team_requires_multiple_roles = "project-decision"
agent_cross_team = "governance-decision"
```

操作性协议意味着：**一个合规的 AOI 可以被编写出来，自动检查这些约束是否被违反。** 这才是"协议"和"文档"的区别。

角色声明也需要从纯 Markdown 变为 TOML 真相源 + Markdown 伴生：

```toml
# roles/collaboration-architect.toml
[role]
name = "collaboration-architect"
domain = "governance+knowledge"

[role.bindings]
rules = ["rules/documentation.md", "rules/context-economy.md"]
skills = ["brainstorming", "writing-plans"]

[role.constraints]
rules_must_exist = true
non_goals_enforced = true
```

---

### Layer 3：世界运行时——哲学内核的正确位置

三层分离后，Ψ=Ψ(Ψ) 和道德经驱动的部分成为 Layer 3，作为**一个具体的 World 实现**而非标准本身。

类比：Linux 标准不规定桌面环境长什么样，但规定了 POSIX 接口。AgentForge 标准不规定世界的哲学内核，但规定了世界如何声明自己的构成法则。

```toml
# Layer 3: AgentForge 世界的 world.toml（完整版）
[world]
name = "agentforge"
version = "3.1.0"
min-alpha = 0.3

[kernel]
manifest = "world.toml"
rules = ["rules/context-economy.md", ...]
references = [
    "docs/references/dao-tech-foundation.md",
]

[kernel.immutable_rules]
world-hierarchy = true
context-economy = true

[fragments.psi-philosophy]
optional = false  # 本世界不可选，但对标准可选
```

而一个采用 Layer 1 的普通项目：

```toml
# Layer 1: 普通项目的 world.toml（最小版）
[world]
name = "my-saas"
version = "1.0.0"

[fragments.backend]
includes = ["rules/api-design.md"]
optional = true
```

两者**同一个 schema**，但消费不同层级。

---

## 五、标准化路线图

### Phase 1：Layer 1 独立发布

```
Phase 1: Layer 1 独立发布
├── AGENTS.md 路由格式规范
├── .agents/ 最小目录约定（rules/ + skills/ + docs/）
├── world.toml Layer 1 schema（仅 [world] + [fragments]）
├── SKILL.md 规范（含 glob frontmatter + $ARGUMENTS）
└── 与 AGENTS.md 标准 30+ 工具的兼容性声明
```

Phase 1 是**现在就能发布的**——`.agents/rules/`、`.agents/skills/`、SKILL.md 模板、`world.toml` 基础结构都已经在生产中验证过了。只需要做一次脱钩：把"哲学驱动"从 Layer 1 的必选项变为 Layer 3 的示范项。

### Phase 2：Layer 2 发布

```
Phase 2: Layer 2 发布
├── 协作元模型规范（15 实体 + 双层结构）
├── 操作性约束 schema（constraints.toml：TOML 声明 + 机器校验）
├── roles/ + teams/ 目录约定
└── 合规 AOI 的参考实现接口
```

### Phase 3：Layer 3 作为示范

```
Phase 3: Layer 3 作为示范
├── AgentForge 世界的完整 world.toml
├── 哲学-工程映射作为 psi-philosophy fragment 示范
├── 记忆做梦协议作为 memory fragment 示范
└── kernel/ 管理规范作为高级特性示范
```

### 补充：参考实现与工具链（Phase 1 持续迭代）

```
├── CLI 工具：world init / world validate / world doctor
├── CI 集成：GitHub Action 自动校验项目是否符合标准
├── IDE 插件：VS Code / JetBrains 对 .agents/ 的语法支持
├── Fragment Registry（共享可插拔规则片段）
├── 与其他工具对话（Cursor / Claude / Copilot 的适配层）
└── 标准化提案（向 AI 编码工具厂商推广 .agents/ 目录约定）
```

---

## 六、v0.1 → v0.2 关键跃迁总结

| 维度 | v0.1 | v0.2 |
|------|------|------|
| 架构 | 渐进式复杂度 Level 0-4（垂直堆叠） | 正交三层 Layer 1/2/3 + Level 0-4 |
| 哲学内核 | kernel 必需，`optional = false` | Layer 3 fragment，对世界不可选，对标准可选 |
| 协作约束 | 自然语言声明 | `constraints.toml` 声明式协议（AOI 可自动校验） |
| SKILL.md | 纯 Markdown | + YAML frontmatter（description/paths/argument-hint） |
| 条件加载 | 路由表唯一机制 | 路由表 + glob frontmatter 双机制正交并存 |
| 角色声明 | 纯 Markdown | TOML 真相源 + Markdown 伴生 |
| world.toml | 固定三层 schema | 按 Layer 渐进 schema（L1 仅 `[world]`+`[fragments]`） |
| 标准化路径 | 无 | Phase 1/2/3 三阶段发布 |

---

## 七、需要回答的核心决策

1. **名字策略**：继续叫 "AGENTS.md 标准"（与 Codex 共享命名空间），还是独立命名？
2. **规范治理**：谁来维护规范？单人项目 vs 开放治理（类似 CommonMark 之于 Markdown）？
3. **最小可行标准**：如果只标准化一件事让全行业采用，是什么？（**世界层级继承** + **kernel 不可变约束**是真正的差异化价值）
4. **渐进式采纳**：能否让一个只用 Codex 的开发者**零成本**开始，然后逐步解锁 `.agents/` 的高级能力？

---

## 总结

AgentForge 的设计是从"世界"自上而下构建的，**完整性很强但可拆性不够**。要做通用标准，需要反过来——**先定义 Layer 1 的最小协议让任何人零前提采用，再让 Layer 2/3 成为渐进升级路径**。AGENTS.md 标准的成功证明了"最小公约数优先"是对的；`.agents/` 证明了"完整语义建模"是可能的。两者结合，才是标准化的正确姿势。
