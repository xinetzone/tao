# AGENTS.md 与 .agents/ 设计哲学

```{topic} 文档定位
本文是 AgentForge 设计哲学专栏文章，系统阐述 `AGENTS.md + .agents/` 双层体系的核心理念、架构设计与行业定位。适合希望深入理解 AgentForge 设计决策的架构师、贡献者和标准采纳者。
```

---

## 1. 为什么需要 AGENTS.md

现代 AI 编码工作流已从"一次性问答"演进为多步骤自主协作：Agent 读取仓库 → 理解架构 → 制定计划 → 修改代码 → 跑测试 → 修复问题 → 总结变更。这需要一种仓库内的"Agent 操作手册"。

`AGENTS.md + .agents/` 本质上在解决一个问题：**如何把人类团队的工程约定、项目上下文、工具边界、执行流程稳定地传递给不同 AI Agent，并让它们在多轮、多工具、多仓库协作中保持一致行为。**

| 文件/目录 | 类比 |
|---|---|
| `README.md` | 给人看的项目入口 |
| `CONTRIBUTING.md` | 给贡献者看的协作规范 |
| `.github/workflows/` | 给 CI/CD 的自动化规则 |
| `AGENTS.md` | 给 AI Agent 看的工作说明书 |
| `.agents/` | 给 AI Agent 的模块化上下文、角色、流程、技能定义 |

---

## 2. AGENTS.md 核心定位

### 2.1 四层价值

1. **给 Agent 明确项目规则** — 技术栈、架构边界、代码风格、测试命令、禁止事项、安全约束
2. **减少重复说明** — 不用每次都告诉 Agent "不要改这个目录""我们用 pnpm 不用 npm"
3. **跨工具共享上下文** — Claude Code、OpenAI Codex CLI、Cursor、Aider 等均可读取
4. **降低误操作风险** — 明确哪些文件不能碰、哪些命令不能运行、哪些行为必须先确认

### 2.2 操作手册，而非组织叙事

Agent 需要的不是公司使命和系统历史，而是：

- 入口在哪里、哪些命令可以跑
- 哪些目录负责什么、什么不能改
- 修改后如何验证
- 当前项目偏好的实现方式
- 遇到不确定时如何决策

**`AGENTS.md` 应该像 checklist，而不是价值观宣言。**

### 2.3 好的 AGENTS.md 判断标准

| 标准 | 说明 |
|------|------|
| **短** | 100～200 行以内 |
| **稳定** | 避免临时内容，放 issue/PR/spec |
| **明确** | 不要"使用最佳实践"，应给出具体命令 |
| **可执行** | Agent 能根据它直接行动 |
| **分层** | 复杂内容链接到 `.agents/` |
| **无冲突** | 不要同时写"用 npm"和"用 pnpm" |
| **面向风险** | 明确高风险行为约束 |

---

## 3. 双层体系架构

### 3.1 AGENTS.md：根契约 + 上下文路由器

`AGENTS.md` 不做"大杂烩"，而是充当根契约 + 上下文路由器：

```{mermaid}
graph TD
    A["AGENTS.md 根契约"] --> B[".agents/rules/ 执行规则"]
    A --> C[".agents/workflows/ 流程模板"]
    A --> D[".agents/skills/ 可复用能力"]
    A --> E[".agents/docs/ AI专属知识库"]
```

它通过映射表告诉 AI 不同任务该读什么文件，实现按需加载而非一次性塞满上下文窗口。

### 3.2 .agents/：模块化上下文库

`.agents/` 负责长文档、特定角色、特定任务、深层架构说明和复杂策略。推荐结构：

```
AGENTS.md              # 必须存在，作为主入口
.agents/
  README.md            # 目录结构与职责说明
  rules/               # 特定领域规范
  workflows/           # 流程化工作流
  skills/              # 可执行技能（每个技能有独立目录 + SKILL.md）
  roles/               # 职责模板
  teams/               # 团队治理（可选）
  context/             # Agent 摘要化上下文
  policies/            # 硬约束
  templates/           # 复用模板
  docs/                # AI 专属知识库
  scripts/             # 自动化校验脚本
```

### 3.3 单文件优先，目录增强

```
AGENTS.md              # 必须存在
.agents/               # 可选，复杂项目再引入
```

单文件入口更容易被工具发现，也更容易被人类理解。**AGENTS.md 负责简明概览和总规则；.agents/ 负责深层细节。**

---

## 4. 五大设计方向

### 4.1 分层指令与优先级

在 monorepo 中支持多层 `AGENTS.md`，优先级规则：

```
用户当前指令 > 子目录 AGENTS.md > 根目录 AGENTS.md > 默认工具规则
```

越靠近代码目录，规则越具体。

### 4.2 可执行工作流

对 Agent 帮助很小的写法：

```markdown
Please write good code.
Follow best practices.
```

对 Agent 帮助很大的写法：

```markdown
## After Editing
Run the following when relevant:
- pnpm typecheck
- pnpm lint
- pnpm test

If any command fails, fix the issue or explain why it is unrelated.
```

### 4.3 命令风险分级

```markdown
## Safe Commands（无需确认）
- pnpm test / pnpm lint / pnpm typecheck
- git diff / git status

## Confirmation Required（需确认）
- database migrations
- dependency upgrades
- deployment commands

## Forbidden（禁止）
- rm -rf /
- commands that expose secrets
- production deploys without explicit approval
```

### 4.4 上下文最小化

```
AGENTS.md           → 只放稳定、关键、高频规则
.agents/context/    → 放低频但重要的背景资料
docs/               → 放人类文档
代码自身             → 作为最终事实来源
```

`AGENTS.md` 不应该代替文档系统，也不应该代替代码搜索。

### 4.5 与现有工具的关系

```
AGENTS.md                      # canonical source（中立、通用、稳定的源头）
.github/copilot-instructions.md # thin wrapper / pointer
.cursor/rules/...              # tool-specific adaptation
.claude/...                    # tool-specific adaptation
```

**`AGENTS.md` 做中立、通用、稳定的源头；其他工具配置引用或同步它。**

---

## 5. 六大核心组件

### 5.1 rules/ — 领域规范

规则文件应写**硬性的、可被 Agent 直接执行的约束**。按领域拆分，每个文件职责单一。

核心高价值规则示例：
- `context-economy.md`：上下文节省策略——把"上下文有限"这个 AI 物理约束转化为项目组织的架构原则
- `skills.md`：技能开发规范，有完整验证体系支撑
- `python.md`：Python 开发规则

### 5.2 workflows/ — 任务流程模板

**Bugfix Workflow**：

```markdown
1. Reproduce or understand the failure.
2. Identify the smallest likely cause.
3. Inspect nearby tests and similar code.
4. Make the smallest safe fix.
5. Add regression coverage when practical.
6. Run relevant checks.
7. Summarize root cause and fix.
```

**Feature Workflow**：

```markdown
1. Identify existing patterns.
2. Locate domain model and API boundaries.
3. Implement backend or data changes first if needed.
4. Implement UI/API integration.
5. Add tests for behavior.
6. Run lint, typecheck, and relevant tests.
7. Summarize user-visible behavior.
```

### 5.3 skills/ — 可执行技能标准闭环

每个技能包含：SKILL.md（标准化描述）、scripts/（实现代码）、tests/（测试）、schemas/（JSON Schema）、evals/（评测集）。

Skills 是 `.agents/` 中**唯一有完整"文档 + 脚本 + 测试 + 评估"闭环的子系统**，是 AgentForge 相对于 Cursor/Claude Code 的真正差异化资产——**平台无关的声明式技能标准**。

### 5.4 roles/ — 职责边界

`roles` 定义职责边界和避规项，而非"人格设定"：

```markdown
## Responsibilities
- React component implementation
- UI state management

## Must Check
- Existing components before creating new ones
- Design tokens

## Avoid
- Business logic inside presentational components
- Unapproved UI libraries
```

### 5.5 teams/ — 多 Team 治理

定义多 Team 的治理边界与跨 Team 协作策略。至少有两个 Team 才能使 Cross-Team Policy 有意义。

### 5.6 docs/ + scripts/ — 知识沉淀与自动化

- `docs/`：AI 专属知识库，长期知识沉淀
- `scripts/`：自动化校验脚本（`check_env.py`、`check_doc_links.py`、`validate_skill_md.py` 等），构成**可自动化的质量门禁**

---

## 6. 渐进式复杂度模型（Level 0-4）

AgentForge Spec 将渐进路径系统化为五个 Level：

```
Level 0 → AGENTS.md（单文件，Codex 兼容）
Level 1 → + .agents/rules/（领域规则拆分）
Level 2 → + .agents/ 完整目录（skills, workflows, scripts, templates, docs）
Level 3 → + world.toml（世界声明 + kernel/fragments 分层）
Level 4 → + 多世界继承 + roles/teams（协作元模型）
```

| 级别 | 适用场景 | 典型规模 | 核心收益 |
|------|---------|---------|---------|
| Level 0 | 个人项目/快速原型 | 1人/<10文件 | 5秒上手，AI行为基线约束 |
| Level 1 | 团队协作 | 2-5人/中型代码库 | 按领域隔离规则 |
| Level 2 | 技能驱动 | 5-20人/含自动化 | 技能+工作流标准化管理 |
| Level 3 | 治理级 | 20+人/开源 | 内核保护+可插拔能力 |
| Level 4 | 多团队/monorepo | 多团队/多子项目 | 规则继承+覆盖控制+角色治理 |

**五大设计目标**：

1. **渐进采纳**：每级独立可用
2. **向下兼容**：Level 0 兼容 OpenAI Codex CLI
3. **向上扩展**：高级特性不破坏低级用法
4. **工具无关**：纯文件约定，不绑定特定 AI 工具
5. **物理隔离**：人类文档（`docs/`）与 AI 知识库（`.agents/docs/`）分离

---

## 7. World 容器与声明式世界描述

### 7.1 world.toml 三层划分

`world.toml` 把项目级 AI 配置提升到**运行时容器**的层面：

| world.toml 层级 | 软件架构对应 | 设计意图 |
|----------------|-------------|---------|
| `kernel`（不可缺的最小世界） | Core Domain | 任何子世界继承都不能破坏的根基 |
| `fragments`（可选能力组合） | Feature Modules | 可安装/卸载不影响基本运行 |
| `memory`（不可移植的个体经验） | Local State / Cache | 项目特有，不随世界迁移 |

**Kernel 准入标准**：不可或缺性、普适性、稳定性。`immutable_rules` 中列出的规则在任何子世界不可覆盖。

### 7.2 多世界继承

Agent 从工作目录向上逐级查找 `AGENTS.md`，每遇到一个即注册为一个世界层级。子世界自动继承祖先世界规则，并可通过显式声明覆盖。覆盖粒度支持文件级、Section 级、路由表行级。推荐嵌套深度 ≤ 3 层。

### 7.3 Registry 与技能分发

```toml
[registries.local]
url = "../registry-index"

[registries.default]
url = "https://github.com/agentforge/registry-index"
```

配合 fragments 分发机制，形成 **AI 规则的 npm/pip** — 声明式能力包管理。

---

## 8. 协作元模型

### 8.1 语义层次

```
Team → Role → Agent → Task → Workflow → Handoff
                        ↓
                Memory / Context / Rule / Skill / Artifact
                        ↓
                Policy / Permission / Session
```

这个元模型定义了：

- **组织层**（Team/Role/Agent）：定义谁做什么
- **执行层**（Mission/Task/Workflow/Handoff）：定义怎么做
- **知识层**（Memory/Context/Rule/Skill/Artifact）：定义用什么
- **治理层**（Policy/Permission）：定义边界在哪
- **运行态**（Session）：定义当前状态

### 8.2 文档边界：人机物理隔离

| 受众 | 目录 | 内容 |
|------|------|------|
| 人类 | `docs/tech/` | API 文档、部署指南、构建规范 |
| 人类 | `docs/general/` | 哲学、数学、通用知识 |
| AI | `.agents/docs/` | AI 专属知识库、架构摘要 |
| AI | `.agents/rules/` | 高频执行规则、约定 |
| 人+AI | `specs/` | 规范文档（公约数） |

---

## 9. 行业格局与差异化

### 9.1 三大流派

| 维度 | AGENTS.md 标准（开放） | Claude Code | AgentForge |
|------|----------------------|-------------|------------|
| 定位 | "AI 的 README" | 项目配置 | "AI 智能体的世界" |
| 入口 | AGENTS.md（扁平） | CLAUDE.md（路由） | AGENTS.md（路由契约） |
| 技能 | 不涉及 | .claude/skills/ | .agents/skills/+评测 |
| 协作 | 不涉及 | 工具白名单 | 协作元模型 |
| 声明式配置 | 无 | settings.json | world.toml |
| 条件加载 | 嵌套 AGENTS.md | paths: glob | 路由表+glob |
| 支持方 | OpenAI/Google/30+ | 仅 Claude Code | 自研 |

### 9.2 AgentForge 的差异化优势

```{mermaid}
flowchart LR
    A["AGENTS.md<br/>全局契约 + 路由"] --> B[".agents/rules/<br/>领域规则"]
    A --> C[".agents/workflows/<br/>工作流"]
    A --> D[".agents/docs/<br/>AI 知识库"]
    A --> E[".agents/skills/<br/>技能资产"]
```

| 维度 | 行业主流 | AgentForge |
|------|---------|------------|
| 契约形式 | 自由文本 Markdown | 路由表 + 结构化 TOML |
| 规则组织 | 散落文件 + Glob | kernel/fragments/capabilities 分层 |
| 文档边界 | 无区分 | docs/（人）↔ .agents/（AI）物理隔离 |
| 能力分发 | 几乎无 | Registry + fragments 包管理 |
| 协作模型 | 单 Agent | 完整 Team/Role/Agent 元模型 |

### 9.3 条件加载双范式

| 范式 | 代表 | 机制 | 优势 | 劣势 |
|------|------|------|------|------|
| Glob 匹配 | Claude Code | `paths: ["src/api/**/*.ts"]` | 无需中央路由、自动触发 | 仅按文件路径 |
| 路由表 | AgentForge | 任务类型→必读入口映射 | 可按语义路由 | 依赖AI主动读取 |

两者不互斥：glob 适合 IDE 集成自动注入，路由表适合 CLI/对话式按需加载。

---

## 10. 深层设计洞见

### 10.1 递归自指是工程实践

整个 `.agents/` 目录本身是一个**元系统**：用文档定义如何管理文档，用规则规定如何编写规则。`check_world_hierarchy.py` 的存在说明递归结构是被主动维护的。当 AI 辅助开发进入深水区，"项目的自我描述能力"成为关键竞争力。

### 10.2 形式化治理与实用主义的张力

`skills/` 和 `scripts/` 是**现在就能跑**的实用层；`roles/` / `teams/` 是**未来才能跑**的治理层。这种张力是**有意为之**——用超前设计的骨架牵引实用层的演进方向，避免短视堆砌。

### 10.3 上下文节省是架构约束

`context-economy.md` 不只是给 AI 的操作指南，它在**约束整个项目的信息架构**：

- 为什么 `docs/tech/` 和 `docs/general/` 必须物理隔离？——因为 AI 需要"检索定位"领域
- 为什么规则拆成多个独立文件？——因为 AI 应该"只读取相关片段"
- 为什么有长期沉淀目录？——因为"稳定知识应沉淀到规则文件中"

**AgentForge 把"上下文有限"这个 AI 的物理约束，转化为了项目组织的架构原则。**

### 10.4 反脆弱设计

`scripts/validation/` 下的校验脚本在**校验元数据的一致性**。当项目足够复杂时，"描述项目的元数据"本身会变成维护负担，AgentForge 的应对方式是**元数据的自动化校验**，形成自我维护的反馈环。

### 10.5 Layer × Level 正交矩阵

```
           Layer 1        Layer 2        Layer 3
Level 0   AGENTS.md        —              —
Level 1   + rules/        + roles/        —
Level 2   + skills/       + workflows/    —
Level 3   + world.toml    + constraints   + kernel/
Level 4   + glob fmtmtr   + 操作性校验    + 做梦协议
```

任何人都可以在矩阵上定位自己的需求，不被"All or Nothing"绑架。**最大的价值不是定义了 Level 4 有多强大，而是定义了 Level 0 有多简单。**

### 10.6 constraints.toml：规范即代码

```toml
[constraints.strong]
agent_requires_role = true
task_requires_mission = true
workflow_owns_no_knowledge = true
```

把自然语言约束变为**声明式布尔值**，使 AOI 可自动校验、CI 可阻断违规、违反时行为确定（strong → ERROR，weak → WARN）。

### 10.7 从世界中心主义到标准中心主义

> v0.1："你进入 AgentForge 的世界，就能获得一切。"
> v0.2："你用 AgentForge 的标准，底层可以是任何实现。"

类比：POSIX 是标准，Linux 是具体实现。AgentForge 选择让自己成为"可被替换的实现"。

---

## 11. 设计原则总结

> 现代 `AGENTS.md + .agents/` 的最佳设计，是把仓库变成一个"Agent 可协作"的工程环境：`AGENTS.md` 提供稳定入口和硬规则，`.agents/` 提供按角色、任务、上下文、策略拆分的模块化知识。它不是单纯提示词，而是 AI 时代的工程协作协议。

十条可操作原则：

1. **`AGENTS.md` 是入口，不是垃圾桶** — 只放稳定、关键、高频规则
2. **`.agents/` 是模块化上下文，不是提示词坟场** — 每个文件有清晰职责
3. **规则要可执行** — checklist 优于"best practices"宣言
4. **风险边界要明确** — 命令分级（Safe / Confirmation Required / Forbidden）
5. **命令要具体** — 给出可复制运行的精确命令
6. **上下文要分层** — AGENTS.md（高频）→ .agents/context/（低频）→ docs/（人类参考）
7. **项目规范应版本化** — 可审查、可共享、可迁移，不应只存在 Agent memory
8. **越靠近代码，规则越具体** — 子目录 AGENTS.md 覆盖父目录规则
9. **中立源头** — AGENTS.md 做通用规范，其他工具引用或同步
10. **先 Markdown，后 schema；先轻量，后自动化** — 不要一开始就过度设计

---

## 12. 未来方向与标准化路线

### 12.1 三阶段演进路径

| 阶段 | 形式 | 特征 |
|------|------|------|
| 第一阶段 | 人类可读 Markdown | 极简但有效 |
| 第二阶段 | Markdown + YAML frontmatter | 结构化元数据 |
| 第三阶段 | 结构化 schema | 可编程配置 |

不要太早进入第三阶段，否则配置系统比项目本身还复杂。

### 12.2 标准化路线图

```
Phase 1: 规范冻结与分离
  ├── AGENTS.md Level 0 兼容 Codex
  ├── world.toml 独立 RFC
  └── 独立 spec 仓库 + JSON Schema 验证

Phase 2: 参考实现与工具链
  ├── CLI：world init / validate / doctor
  ├── IDE 插件
  └── CI 集成：GitHub Action

Phase 3: 生态建设
  ├── Fragment Registry（类似 npm registry）
  ├── 官方 Fragment 集合
  └── 与其他工具适配层
```

### 12.3 核心战略优势

1. **技能层对齐 agentskills.io**：在技能层无需重新发明轮子
2. **世界层级继承是独家能力**：无竞品定义多 AGENTS.md 继承 + kernel 不可变 + 覆盖粒度控制
3. **kernel/fragments 分层是独创性贡献**：在 AI Agent 约定领域全新

---

## 13. 设计张力与反思

### 13.1 复杂度 vs 简约性

设计哲学声称"大道至简"，但实际体系相当复杂。**关键问题**：什么场景下复杂体系才能真正值回票价？Level 0-4 渐进模型正是对此的回答——把认知门槛转化为增长路径。

### 13.2 通用标准 vs 内部治理

AgentForge 本质在定义"AI 原生操作系统"的文件约定层。理念有前瞻性，但采纳门槛远高于主流"一个文件搞定"方案。

**核心定位**：AGENTS.md 开放标准是独立的社区标准，AgentForge 定义了该文件的推荐格式和配套目录结构。两者独立，但互操作。

### 13.3 标准战争的胜负

> 所有精妙设计加起来，不如一个能让新用户在 30 秒内尖叫的体验。

npm 的成功不是因为 `package.json` Schema 设计有多优雅，而是因为 `npm install` 太方便了。AgentForge 需要找到自己的"left-pad moment"——`world init` → `world install` → `world validate`，一条命令链搞定。

**规范是骨架，体验是血肉。**
