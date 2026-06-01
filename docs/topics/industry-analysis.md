# AI 智能体契约文件行业对标分析

```{article-info}
:date: 2026-06
:read-time: 15 min
```

## 引言

AI Coding Agent 正从"一次性问答"演进为"仓库级自主工作流"——读取仓库、理解架构、制定计划、修改代码、跑测试、修复问题。这要求一种仓库内的"Agent 操作手册"来稳定传递工程约定。

`AGENTS.md + .agents/` 解决的核心问题：**如何把人类团队的工程约定、项目上下文、工具边界、执行流程稳定地传递给不同 AI Agent，并让它们在多轮、多工具、多仓库协作中保持一致行为。**

---

## 行业主流方案扫描

### 契约文件格局

| 工具/平台 | 契约文件 | 特点 |
|-----------|----------|------|
| **Claude Code** | `CLAUDE.md` | 最早提出"项目级 AI 指令"，自由文本，无严格 Schema |
| **Cursor** | `.cursor/rules/` | 文件拆分、Glob 匹配、`always`/`auto-attached`/`agent-requested` 三级触发 |
| **Windsurf** | `.windsurfrules` | 单文件，CLAUDE.md 简化版 |
| **GitHub Copilot** | `.github/copilot-instructions.md` | 借力 `.github/` 已有约定目录 |
| **OpenAI Agents SDK** | `instructions` + `guardrails` | "指令"与"护栏"分离，面向 Agent 而非项目 |
| **Qoder** | `.qoder/` + rules 系统 | `.qoder/repowiki/` 知识库 + rules 行为约束 |
| **AgentForge** | `AGENTS.md` + `.agents/` + `world.toml` | 完整分层治理体系 |

### 三条行业主线

1. **单文件派**（CLAUDE.md、AGENTS.md）：自由文本承载全局契约，轻量但缺乏结构化
2. **多文件规则派**（`.cursor/rules/`、`.qoder/rules/`）：按领域拆分、按触发条件匹配，类似"AI 的 lint 规则"
3. **完整目录派**（`.agents/`、`.github/`）：将 AI 资产作为独立子系统治理，包含规则、工作流、技能、知识库

### 兼容性矩阵

| 特性 | Codex CLI | Claude Code | Cursor | AgentForge |
|------|-----------|-------------|--------|------------|
| 读取 AGENTS.md | 是 | 忽略 | 忽略 | 是 |
| 解析上下文路由表 | 否 | 否 | 否 | 是 |
| 读取 .agents/rules/ | 否 | 否 | 否 | 是 |
| 解析 world.toml | 否 | 否 | 否 | 是 |
| 世界继承 | 否 | 否 | 否 | 是 |
| 技能 SKILL.md | 否 | 否 | 否 | 是 |

---

## AgentForge 五层设计深度

AgentForge 在"完整目录派"中处于最前沿，其设计可拆为五个递进层次：

```{mermaid}
flowchart LR
    A["AGENTS.md<br/>全局契约 + 路由"] --> B[".agents/rules/<br/>领域规则"]
    A --> C[".agents/workflows/<br/>工作流"]
    A --> D[".agents/docs/<br/>AI 知识库"]
    A --> E[".agents/skills/<br/>技能资产"]
```

### 第 1 层：AGENTS.md = 路由契约

AGENTS.md 不做规则本体，只做路由表。遇到什么任务 → 去读哪个文件。与 Cursor 的 Glob pattern 本质区别：**一个人类可读的上下文路由表，而不是给工具解析的 Glob**。

### 第 2 层：.agents/ = 人机物理隔离

- `docs/` = 人类维度，人类开发者阅读维护
- `.agents/` = AI 维度，AI 智能体消费执行
- 两者通过双向同步保持一致性

行业独创——绝大多数工具把 AI 指令混在项目文件里。AgentForge 认识到：**人读的东西和 AI 需要的东西，信息密度和组织方式天然不同**。

### 第 3 层：world.toml = 声明式世界描述

| world.toml 层级 | 软件架构对应 | 设计意图 |
|----------------|-------------|---------|
| `kernel`（最小世界） | Core Domain | 子世界继承不能破坏的根基 |
| `fragments`（可选能力） | Feature Modules | 可安装/卸载不影响基本运行 |
| `memory`（个体经验） | Local State | 项目特有，不随世界迁移 |

把"AI 项目配置"做成**包管理器式的声明式清单**——行业尚无第二家。这和 Linux Kconfig / `package.json` 的 `dependencies` + `optionalDependencies` 是同一设计范式。

### 第 4 层：Registry + 技能生态

`registry.toml` + `world.toml` + `fragments` 构成完整的包分发模型——**AI 规则的 npm/pip**。

### 第 5 层：协作元模型

```
Team → Role → Agent → Task → Workflow → Handoff
                        ↓
                Memory / Context / Rule / Skill / Artifact
                        ↓
                Policy / Permission / Session
```

四个语义层：
- **组织层**（Team/Role/Agent）：定义谁做什么
- **执行层**（Mission/Task/Workflow/Handoff）：定义怎么做
- **知识层**（Memory/Context/Rule/Skill/Artifact）：定义用什么
- **治理层**（Policy/Permission）：定义边界在哪

---

## 三大流派深度对比

| 维度 | AGENTS.md 开放标准 | CLAUDE.md + .claude/ | AGENTS.md + .agents/（AgentForge） |
|------|-------------------|---------------------|----------------------------------|
| 定位 | "AI 的 README" | Claude Code 项目配置 | "AI 智能体的世界" |
| 入口 | AGENTS.md（扁平） | CLAUDE.md（<200行路由） | AGENTS.md（路由契约 + Mermaid） |
| 规则 | 全部写入口 | .claude/rules/ + paths:glob | .agents/rules/ + 任务路由表 |
| 技能 | 不涉及 | .claude/skills/ + SKILL.md | .agents/skills/ + SKILL.md + 评测 |
| 子智能体 | 不涉及 | .claude/agents/ + 工具白名单 | .agents/roles/ + teams/ + 协作元模型 |
| 声明式配置 | 无 | settings.json（权限/hooks） | world.toml（kernel/fragments/capabilities/memory） |
| 条件加载 | 嵌套 AGENTS.md | paths: frontmatter glob | 任务类型→规范入口路由表 |
| 记忆 | 不涉及 | agent-memory/（自动 MEMORY.md） | docs/superpowers/memories/ |
| 支持方 | OpenAI/Google/Cursor/30+ | 仅 Claude Code | 自研 |

### 条件加载的两种范式

| 范式 | 代表 | 机制 | 优势 | 劣势 |
|------|------|------|------|------|
| Glob 匹配 | Claude Code | `paths: ["src/api/**/*.ts"]` | 无需中央路由、自动触发 | 仅按文件路径 |
| 路由表 | AgentForge | 任务类型→必读入口映射 | 可按语义路由 | 依赖 AI 主动读取 |

两者不互斥：glob 适合 IDE 集成自动注入，路由表适合 CLI/对话式按需加载。

---

## 与行业主流的关键差异

| 维度 | 行业主流（2024-2025） | AgentForge |
|------|----------------------|------------|
| **契约形式** | 自由文本 Markdown | 路由表 + 结构化 TOML |
| **规则组织** | 散落文件 + Glob 匹配 | kernel/fragments/capabilities 分层模型 |
| **文档边界** | 无区分 | docs/（人）↔ .agents/（AI）物理隔离 |
| **能力分发** | 几乎无 | Registry + fragments 包管理 |
| **协作模型** | 单 Agent | 完整 Team/Role/Agent 元模型 |
| **哲学根基** | 无 | Ψ=Ψ(Ψ) + 极简原则 |
| **世界抽象** | 无 | World 作为统一上下文容器，支持多端协同 |

---

## 六个核心洞见

### 洞见一：路由机制——AGENTS.md 是路由器，不是垃圾桶

`AGENTS.md` 的核心职责是**上下文路由**而非知识堆放。它通过映射表引导 Agent 按需加载规则，避免一次性塞满上下文窗口。这与 Claude Code 社区的最佳实践共识一致："CLAUDE.md should be a routing file, not a knowledge dump."

AgentForge 将路由提升为三维触发模型：

```toml
[routing]
intents = ["python", "依赖管理"]           # 任务意图
file_patterns = ["*.py", "pyproject.toml"] # 文件路径
phases = ["execution", "review"]           # 会话阶段
```

### 洞见二：双轨架构——人/AI 文档物理隔离

| 受众 | 目录 | 内容特征 |
|------|------|---------|
| 人类 | `docs/` | 叙述性、背景丰富、示例充分 |
| AI | `.agents/` | 精确、无歧义、快速索引 |

物理隔离 > 语义区分。同一份知识在两个维度的信息密度和组织方式天然不同，强行混合只会两头不讨好。

### 洞见三：声明式世界描述——从配置文件到包管理

`world.toml` 把项目级 AI 配置提升到运行时容器层面：

- **kernel**（不可覆盖的宇宙法则）→ 任何子世界继承都不能破坏
- **fragments**（可组合能力单元）→ 安装/卸载不影响基本运行
- **capabilities**（独立技能）→ 按需加载的执行资产

对应物：Linux Kconfig、npm `package.json`、Python `pyproject.toml`——但面向 AI Agent 项目。

### 洞见四：包管理分发——Registry 是 AI 规则的 npm

AgentForge 通过 `registry.toml` + fragments 建立了完整的分发模型：

```
world install python-engineering    # 安装 Python 工程规范
world fragment init --from-rules    # 将本地规则打包为可分发片段
world publish                       # 发布到远程 Registry
```

降低创作者成本 > 降低消费者成本。npm 成功的核心不是 `npm install` 简单，而是 `npm publish` 简单。

### 洞见五：协作元模型——超越单 Agent 的语义框架

AgentForge 定义了从单 Agent 任务到多 Agent 协作的统一语义框架。当前主流工具（Cursor、Claude Code）只解决"一个 AI 怎么干活"，AgentForge 已为"多个 AI 怎么组队干活"做好底层语义准备。

关键机制：
- **多世界继承**：Agent 从工作目录向上逐级查找 AGENTS.md，每遇到一个即注册为一层世界
- **不可变法则**：`immutable_rules` 在任何子世界不可覆盖
- **覆盖粒度**：文件级、Section 级（`##` 标题）、路由表行级

### 洞见六：哲学根基——上下文节省作为架构约束

`context-economy.md` 不只是给 AI 的操作指南，它在约束整个项目的信息架构：
- 为什么文档物理隔离？——AI 需要先"检索定位"领域
- 为什么规则拆成独立文件？——AI 应该"只读取相关片段"
- 为什么有长期沉淀目录？——"稳定知识应沉淀到规则文件中"

AgentForge 把"上下文有限"这个 AI 的物理约束，转化为**项目组织的架构原则**。

---

## 领先与滞后分析

### AgentForge 明显领先

| 领先方向 | 行业现状 | AgentForge 状态 |
|---------|---------|----------------|
| 人/AI 双轨物理隔离 | 行业几乎无人提及 | 已落地实践 |
| 声明式世界描述（world.toml） | 无竞品定义 | 完整 Schema |
| 协作元模型完整度 | 空白地带 | 语义框架完备 |
| 哲学-工程闭环映射 | 行业独一份 | 持续实践中 |
| 多世界继承 + kernel 不可变 | 无竞品 | 设计完成 |
| kernel/fragments 分层 | AI Agent 约定领域全新 | 独创性贡献 |

### 行业正快速追赶的方向

| 追赶方向 | 竞品动态 | AgentForge 差距 |
|---------|---------|----------------|
| Glob 规则触发 | Cursor 自动按文件匹配 | 依赖 AI 主动路由 |
| `.github/` 借力 | Copilot 降低入驻门槛 | 独立目录认知成本高 |
| 简约传播 | Claude Code 单文件即用 | 完整体系采纳门槛高 |
| Agent SDK 标准 | OpenAI 可能推出官方标准 | 需保持兼容监控 |

### 工程落地差距

| 方向 | AgentForge 现状 | 主流做法 | 差距 |
|------|----------------|----------|------|
| 条件加载 | 路由表（依赖 AI 主动） | glob frontmatter（工具自动） | 可叠加 glob |
| 强制执行 | 全是指导性 Markdown | hooks + permissions | 缺"约定变强制"层 |
| 技能参数 | SKILL.md 静态 | frontmatter + $ARGUMENTS | 缺动态参数 |
| 子智能体记忆 | 手动沉淀模板 | 自动维护 MEMORY.md | 缺自动化闭环 |
| 跨工具兼容 | 仅自研 | AGENTS.md 30+ 工具通用 | 入口兼容，目录需桥接 |

---

## 创新前瞻

### 渐进式复杂度模型（Level 0-4）

```
Level 0 → AGENTS.md（单文件，Codex 兼容）
Level 1 → + .agents/rules/（领域规则拆分）
Level 2 → + .agents/ 完整目录（skills, workflows, scripts）
Level 3 → + world.toml（世界声明 + kernel/fragments 分层）
Level 4 → + 多世界继承 + roles/teams（协作元模型）
```

| 级别 | 适用场景 | 典型规模 | 核心收益 |
|------|---------|---------|---------|
| Level 0 | 个人项目/快速原型 | 1人 / <10文件 | 5 秒上手，AI 行为基线 |
| Level 1 | 团队协作 | 2-5 人 / 中型代码库 | 按领域隔离规则 |
| Level 2 | 技能驱动 | 5-20 人 / 含自动化 | 技能 + 工作流标准化 |
| Level 3 | 治理级 | 20+ 人 / 开源 | 内核保护 + 可插拔能力 |
| Level 4 | 多团队/monorepo | 多团队 / 多子项目 | 规则继承 + 覆盖 + 角色治理 |

### Layer × Level 正交矩阵

任何团队都可以在此矩阵定位需求，不被"All or Nothing"绑架：

- 3 人小团队用 Layer 1 Level 2（AGENTS.md + rules + skills）
- AI 协作需求的团队用 Layer 2 Level 3（加 roles + constraints.toml）
- AgentForge 自身在 Layer 3 Level 4（全部能力）
- **三者共享同一个 AGENTS.md 标准，彼此不冲突**

### constraints.toml：规范即代码

```toml
[constraints.strong]
agent_requires_role = true
task_requires_mission = true
workflow_owns_no_knowledge = true
```

将自然语言约束转为声明式布尔值，实现：
- AOI 自动校验合规性
- CI 阻断违规（如 lint）
- strong → ERROR 阻断，weak → WARN 不阻断

### Skills 跨平台对齐

AgentForge 的 SKILL.md 与 agentskills.io 开放标准对齐，实现：
- 技能可跨平台复用
- 降低创作者维护成本
- 借助 agentskills.io 生态的网络效应

### 标准化战略定位

| 玩家 | 约定 | 状态 | 覆盖范围 |
|------|------|------|---------|
| OpenAI Codex CLI | AGENTS.md | 事实标准，60k+ 仓库 | 扁平指令文件 |
| Anthropic | CLAUDE.md | Claude Code 内置 | 扁平指令 + @file 引用 |
| Cursor | .cursor/rules/*.mdc | 市场领先工具 | 规则文件 + frontmatter |
| agentskills.io | SKILL.md | 开放标准 | 仅技能层 |
| AgentForge | AGENTS.md + .agents/ + world.toml | 提案阶段 | 全栈：内核到多世界继承 |

AgentForge 的战略机会——**成为"AI 原生的 package.json"**：

- `AGENTS.md` = AI 项目的 README（人类可读入口）
- `world.toml` = AI 项目的 package.json（声明式依赖与配置）
- `.agents/` = AI 项目的 node_modules/（实际资产落点）
- Registry = AI 项目的 npm registry（分发网络）

---

## 设计张力与风险

| 张力维度 | 核心问题 | 应对策略 |
|---------|---------|---------|
| 复杂度 vs 简约性 | 完整体系治理成本可能超过效率收益 | Level 0-4 渐进采纳 |
| 跨工具兼容性 | 其他 AI 工具无法理解深层引用 | Layer 1 保持与 Codex 兼容 |
| 通用标准 vs 内部治理 | 采纳门槛远高于"一个文件搞定" | 分离声明：标准独立、实现可替换 |
| 运行时缺失 | 治理层可能变成死文档 | 优先补强 skills/ + scripts/ 可执行层 |

---

## 结论

AgentForge 在 AI 智能体协作约定领域处于设计前沿：
- **理念领先**：五层设计深度、协作元模型、声明式世界描述均无竞品
- **运行时滞后**：roles/teams 缺乏运行时绑定，constraints 缺乏执行器
- **骨架正确**：整体架构为未来多 Agent 协作做好了底层准备

当前状态类似早期 Kubernetes 之前的 Borg 论文阶段——**理念领先、运行时滞后、但骨架正确**。

最大的风险不是"过度设计"，而是**运行时迟迟不来导致治理层变成死文档**。最大的机会是**率先建立跨平台技能标准**，让 `.agents/skills/` 成为 AI 时代的 `package.json`。
