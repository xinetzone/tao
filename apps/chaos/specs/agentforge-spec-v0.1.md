# AgentForge Specification v0.1

> **状态**: Draft | **版本**: 0.1.0 | **日期**: 2026-05-28
>
> 本文档定义 AgentForge 智能体协作目录协议的开放标准。任何项目均可按本规范组织 `AGENTS.md` 与 `.agents/` 目录，以实现 AI 智能体的标准化配置、跨工具互操作与渐进式治理。

---

## 1. 概述与设计目标

### 1.1 背景

当前 AI 编码工具（Codex CLI、Claude Code、Cursor、Copilot 等）各自定义项目级智能体指令的文件约定：

| 工具 | 约定文件 | 特点 |
|------|---------|------|
| OpenAI Codex CLI | `AGENTS.md` | 扁平 Markdown，无结构化分层 |
| Anthropic Claude Code | `CLAUDE.md` | 扁平指令 + `@file` 引用 |
| Cursor | `.cursor/rules/*.mdc` | frontmatter 条件匹配 |
| GitHub Copilot | `.github/copilot-instructions.md` | 单文件 |

这些方案存在三个共性缺陷：

1. **无渐进式复杂度**：要么全用、要么不用，没有中间态
2. **无继承机制**：monorepo 或多团队场景下无法分层复用规则
3. **无内核保护**：任何修改均可被任意覆盖，缺少不可变约束

### 1.2 设计目标

AgentForge Spec 旨在定义一套**渐进式、向后兼容、可继承**的智能体协作目录协议：

- **渐进采纳**：从单文件（Level 0）到完整治理（Level 4），每级独立可用
- **向下兼容**：Level 0 格式兼容 OpenAI Codex CLI 的 `AGENTS.md` 解析预期
- **向上扩展**：高级特性（世界分层、内核保护）不破坏低级用法
- **工具无关**：`.agents/` 目录是纯文件约定，不绑定特定 AI 工具或 IDE

### 1.3 适用范围

本规范适用于：

- 希望在项目中标准化 AI 智能体行为的开发团队
- monorepo 或多项目场景下需要规则继承与覆盖的组织
- AI 编码工具厂商希望支持结构化项目约定
- 技能/规则/工作流的跨平台复用生态

---

## 2. 术语定义

| 术语 | 定义 |
|------|------|
| **World（世界）** | 一个由 `AGENTS.md` + `.agents/` 定义的完整智能体协作空间，对应一个项目或子项目 |
| **Kernel（内核）** | 世界中不可分割的最小文件集合，缺少任一部分则世界不成立 |
| **Fragment（片段）** | 领域内聚的可选能力组合，可安装/卸载而不影响世界基本运行 |
| **Capability（能力）** | 独立安装的技能、脚本和模板，位于最外层 |
| **Rule（规则）** | 面向特定领域（Python、前端、文档治理等）的行为约束文件 |
| **Workflow（工作流）** | 多步骤流程化任务定义（如 PR Review、角色审查） |
| **Skill（技能）** | 智能体可执行的独立能力单元，遵循 `SKILL.md` 标准 |
| **Role（角色）** | 协作元模型中的职责模板，定义责任边界与默认绑定 |
| **Team（团队）** | 协作元模型中的治理边界，包含角色成员关系与协作策略 |
| **Root World（根世界）** | 层级树顶点，其 Kernel 约束对所有子世界生效 |
| **Child World（子世界）** | 继承父世界规则并可声明覆盖的子级协作空间 |

---

## 3. 渐进式复杂度模型

本规范定义五个递进级别，项目可按需选择采纳深度。每个级别向下兼容且独立可用。

```
Level 0 ─── AGENTS.md（单文件，Codex 兼容）
  │
Level 1 ─── + .agents/rules/（领域规则拆分）
  │
Level 2 ─── + .agents/ 完整目录（skills, workflows, scripts, templates, docs）
  │
Level 3 ─── + world.toml（世界声明 + kernel/fragments 分层）
  │
Level 4 ─── + 多世界继承 + roles/teams（协作元模型）
```

### 级别选择指南

| 级别 | 适用场景 | 典型项目规模 | 核心收益 |
|------|---------|------------|---------|
| **Level 0** | 个人项目、快速原型 | 1 人 / <10 文件 | 5 秒上手，AI 行为基线约束 |
| **Level 1** | 团队协作项目 | 2-5 人 / 中型代码库 | 按领域隔离规则，降低维护成本 |
| **Level 2** | 技能驱动项目 | 5-20 人 / 含自动化流水线 | 技能+工作流+脚本的标准化管理 |
| **Level 3** | 治理级项目 | 20+ 人 / 开源项目 | 内核保护 + 可插拔能力片段 |
| **Level 4** | 多团队 / monorepo | 多团队 / 多子项目 | 规则继承 + 覆盖控制 + 角色治理 |

### 级别依赖规则

1. 高级别**必须**包含所有低级别的必要文件
2. 高级别**不得**破坏低级别的兼容性约束
3. 工具**可以**仅实现部分级别，但必须声明所支持的级别
4. 项目**可以**在不同子目录使用不同级别（参见 Level 4）

---

## 4. Level 0 — 基础指令（AGENTS.md）

### 4.1 目标

在项目根目录放置一个 `AGENTS.md` 文件，为所有 AI 智能体提供全局行为约束。**此格式与 OpenAI Codex CLI 完全兼容**。

### 4.2 文件位置

```
project-root/
├── AGENTS.md          ← 必需：全局智能体指令
└── ...（项目文件）
```

### 4.3 格式要求

`AGENTS.md` 是一个标准 Markdown 文件，遵循以下约束：

1. **文件名**：必须为 `AGENTS.md`（大小写敏感）
2. **位置**：必须位于项目根目录（版本控制仓库的顶层目录）
3. **编码**：UTF-8
4. **内容**：纯 Markdown，无 frontmatter 要求

### 4.4 推荐结构

```markdown
# 项目名称 — AI 智能体指令

## 项目概述
（简要描述项目用途、技术栈、核心功能）

## 全局规则
- 沟通语言：（如中文/英文）
- 代码风格：（如 PEP 8 / Google Style）
- 依赖管理：（如 uv / npm / pnpm）

## 项目结构
（描述关键目录的职责）

## 开发约定
（描述提交规范、测试要求、审查流程等）
```

### 4.5 Codex 兼容性约束

为确保与 OpenAI Codex CLI 兼容：

- `AGENTS.md` 文件**前部**应为自包含的纯文本指令，不依赖外部文件引用即可理解核心约束
- 可使用相对路径引用其他文件（如 `[规则](.agents/rules/python.md)`），但不识别 `.agents/` 的工具将忽略这些引用
- 不得要求解析 TOML/YAML 等非 Markdown 格式才能获取基本行为约束

---

## 5. Level 1 — 领域规则拆分

### 5.1 目标

将 `AGENTS.md` 中的领域规则拆分为独立文件，按任务类型按需加载，降低 token 消耗。

### 5.2 文件结构

```
project-root/
├── AGENTS.md              ← 全局入口 + 上下文路由表
├── .agents/
│   └── rules/             ← 领域规则文件
│       ├── python.md
│       ├── frontend.md
│       ├── documentation.md
│       └── ...
└── ...
```

### 5.3 .agents/ 目录约束

1. **目录名**：必须为 `.agents`（以点开头的隐藏目录）
2. **位置**：必须与 `AGENTS.md` 同级
3. **编码**：所有文件 UTF-8

### 5.4 规则文件约定

- 文件名使用小写 + 连字符：`context-economy.md`、`data-flow-ordering.md`
- 每个文件聚焦**单一领域**
- 文件内部使用标准 Markdown 结构

### 5.5 上下文路由表

`AGENTS.md` 中**应当**包含上下文路由表，声明任务类型与规则文件的映射：

```markdown
## 上下文路由

| 任务类型 | 必读入口 |
|---|---|
| Python 开发、依赖管理 | `.agents/rules/python.md` |
| 前端开发 | `.agents/rules/frontend.md` |
| 文档治理 | `.agents/rules/documentation.md` |
```

路由表是**建议性**的：不识别路由的工具仍可正常使用 `AGENTS.md` 本身的内容。

---

## 6. Level 2 — 完整目录结构

### 6.1 目标

引入技能、工作流、脚本、模板和知识库的标准化目录管理。

### 6.2 文件结构

```
project-root/
├── AGENTS.md
├── .agents/
│   ├── README.md          ← 目录说明（推荐）
│   ├── rules/             ← 领域规则（Level 1）
│   ├── skills/            ← 技能目录
│   │   └── <skill-name>/
│   │       ├── SKILL.md   ← 必需：技能文档
│   │       ├── scripts/   ← 推荐：实现脚本
│   │       └── tests/     ← 推荐：测试
│   ├── workflows/         ← 工作流定义
│   ├── scripts/           ← 自动化脚本
│   ├── templates/         ← 标准化模板
│   └── docs/              ← AI 专属知识库
└── ...
```

### 6.3 各目录职责

| 目录 | 必需性 | 职责 |
|------|--------|------|
| `rules/` | 必需（Level 1+） | 按领域拆分的智能体行为约束 |
| `skills/` | 可选 | 可执行的独立能力单元，每个子目录包含 `SKILL.md` |
| `workflows/` | 可选 | 多步骤流程化任务定义 |
| `scripts/` | 可选 | 供智能体调用的自动化校验或执行脚本 |
| `templates/` | 可选 | 供开发者和智能体复用的标准化模板 |
| `docs/` | 可选 | AI 专属知识库、架构分析与参考文档 |
| `README.md` | 推荐 | `.agents/` 目录的定位、功能说明与导航 |

### 6.4 SKILL.md 标准

技能文档应遵循 [Agent Skills 开放标准](https://agentskills.io)，并至少包含以下章节：

1. **Skill ID** — 全局唯一标识，与目录名一致
2. **Description** — 功能描述与使用场景
3. **I/O Parameters** — 输入输出参数定义
4. **Dependencies** — 运行依赖
5. **Deployment** — 部署步骤
6. **Error Handling** — 错误处理规范
7. **Changelog** — 版本记录

### 6.5 技能目录结构

```
skills/<skill-name>/
├── SKILL.md           # 必需：技能文档
├── scripts/           # 推荐：实现脚本
├── tests/             # 推荐：测试文件
├── schemas/           # 可选：JSON Schema
├── references/        # 可选：参考文档
└── evals/             # 可选：评测集
```

---

## 7. Level 3 — 世界声明与分层

### 7.1 目标

引入 `world.toml` 声明式描述文件，将世界资产分为 Kernel（不可变内核）、Fragments（可插拔片段）和 Capabilities（独立能力）三层。

### 7.2 文件结构（增量）

```
.agents/
├── world.toml         ← 必需（Level 3）：世界声明
├── kernel/            ← 推荐：内核边界管理元数据
│   └── README.md
├── rules/
├── skills/
├── ...
└── docs/
    └── references/    ← kernel 引用的参考文档
```

### 7.3 world.toml 概览

`world.toml` 是世界的声明式 manifest，定义世界的身份、内核组成、可选片段和能力声明。完整 Schema 见 [第 10 节](#10-worldtoml-schema)。

### 7.4 三层资产模型

```
┌─────────────────────────────────────────┐
│  Kernel（不可变内核）                      │
│  ─ 缺少任一部分则世界不成立                 │
│  ─ 子世界禁止覆盖                         │
│  ─ 变更频率极低，等同于"修改物理定律"        │
├─────────────────────────────────────────┤
│  Fragments（可插拔片段）                   │
│  ─ 领域内聚的可选能力组合                   │
│  ─ 可安装/卸载，不影响世界基本运行           │
│  ─ 每个片段声明版本和包含文件列表            │
├─────────────────────────────────────────┤
│  Capabilities（独立能力）                  │
│  ─ 技能、独立脚本、模板                    │
│  ─ 最细粒度的可插拔单元                    │
│  ─ 对应 skills/、templates/ 等目录         │
└─────────────────────────────────────────┘
```

### 7.5 Kernel 准入与退出标准

**准入条件（全部满足）**：

1. **不可或缺性**：移除后世界丧失基本运行能力
2. **普适性**：所有 Agent（无论领域）都必须遵循
3. **稳定性**：变更频率极低

**退出条件（任一满足）**：

1. 仅特定领域的 Agent 需要遵循
2. 移除后世界仍能基本运行
3. 变更频率较高且不影响其他 Agent

### 7.6 Kernel 不可覆盖约束

- `world.toml` 中 `[kernel]` 声明的条目为**宇宙法则**
- `immutable_rules` 字段列出的规则文件，在任何子世界中**不可覆盖**
- 子世界只允许通过 Fragment 扩展与 Kernel 交互，禁止修改已有内容
- Agent 检测到子世界试图覆盖 Kernel 条目时，**必须**显式报告冲突并拒绝执行

---

## 8. Level 4 — 多世界继承与协作元模型

### 8.1 目标

支持 monorepo 或多子项目场景下的世界发现、规则继承、覆盖控制与角色/团队治理。

### 8.2 多世界发现规则

Agent 启动时从当前工作目录向上逐级查找 `AGENTS.md`：

1. 每遇到一个 `AGENTS.md` 即注册为一个**世界层级**（World Layer）
2. 根目录的 `AGENTS.md` 为**根世界**（Root World）
3. 查找在到达文件系统根时终止

```
filesystem-root/
├── AGENTS.md                    ← Root World（宇宙根世界）
├── .agents/
│   └── world.toml
├── project-a/
│   ├── AGENTS.md                ← Child World A（继承 + 覆盖）
│   └── .agents/
└── project-b/
    ├── AGENTS.md                ← Child World B（继承 + 覆盖）
    └── .agents/
```

### 8.3 继承语义

- 子世界**自动继承**所有祖先世界的规则
- 子世界中**显式声明**的同名规则覆盖父世界对应规则
- 未声明覆盖的规则**原样透传**至子世界
- 优先级链：`当前目录 > 父目录 > … > Root World`

### 8.4 覆盖粒度

| 覆盖对象 | 最小单位 | 覆盖方式 |
|---|---|---|
| `.agents/rules/` 下的规则文件 | 文件（按文件名匹配） | 子世界同名文件完整覆盖 |
| 规则文件内部的规则节 | Section（`##` 级标题） | 子世界同节声明覆盖 |
| 上下文路由表 | 表格行（按 key 匹配） | 追加或覆盖，未提及项透传 |

### 8.5 子世界目录语义

| 子目录 | 语义 | 继承行为 |
|---|---|---|
| `.agents/rules/` | 增量覆盖规则 | 同名文件覆盖父世界；无同名则透传 |
| `.agents/skills/` | 附加技能集 | **追加**到父世界技能集 |
| `.agents/workflows/` | 附加工作流 | **追加**到父世界工作流集 |
| `world.toml` | 世界 manifest | **monorepo 仅允许一份**，子目录禁止独立 `world.toml` |

### 8.6 嵌套深度约束

- 推荐嵌套深度 **≤ 3 层**
- 超过 3 层时应评估治理成本与规则冲突风险

### 8.7 覆盖说明

子世界 `AGENTS.md` **可以**声明 `## 覆盖说明` 节，列出有意覆盖的父规则：

```markdown
## 覆盖说明

| 父规则文件 | 覆盖节 | 覆盖原因 |
|---|---|---|
| `python.md` | `## 3. 版本约束` | 子项目锁定 Python 3.11 |
```

未声明的隐式覆盖合法，但审计时应标记为待审项。

### 8.8 协作元模型

Level 4 引入 Role（角色）和 Team（团队）作为协作治理的语义实体。

#### 角色（Role）

```
.agents/
├── roles/
│   ├── README.md              ← 角色框架定义
│   └── <role-name>.md         ← 角色实例
```

角色文件必须包含：

- **Role Identity**：角色名称与所属领域
- **Responsibilities**：核心职责边界
- **Default Bindings**：默认绑定的规则、参考页与能力资产
- **Non-Goals**：明确不属于该角色的范围

#### 团队（Team）

```
.agents/
├── teams/
│   ├── README.md              ← 团队框架定义
│   └── <team-name>.md         ← 团队实例
```

团队文件定义：

- **Team Identity**：团队名称与治理范围
- **Members**：角色成员关系
- **Collaboration Strategy**：跨团队协作策略

#### 元模型核心约束

- `Team` 是治理边界，`Role` 是职责模板，`Agent` 是执行主体
- `Agent` 必须通过 `Role` 进入规范性协作体系
- `roles/` 和 `teams/` 是协作元模型的语义实例目录

---

## 9. AGENTS.md 格式规范

### 9.1 文件结构（完整规范）

```markdown
# [项目名称] — AI 智能体指令

（纯文本全局规则——此部分必须自包含，兼容 Codex 解析）

## 1. 全局核心规则
（通信语言、代码风格、依赖管理等基础约束）

## 2. 项目结构入口
（关键目录说明，可选引用 .agents/README.md）

## 3. 协作元模型
（Level 4 项目：角色/团队摘要与引用）

## 4. 上下文路由
（任务类型 → 规则文件映射表）

## 5. 文档与产物边界
（README.md / docs/ / .agents/docs/ 的职责划分）

## 6. 工具与脚本
（自动化脚本位置与调用方式）

## 7. 覆盖说明
（Level 4 子世界：列出有意覆盖的父规则）
```

### 9.2 兼容性分区

`AGENTS.md` 内容分为两个语义区域：

| 区域 | 范围 | 解析要求 |
|------|------|---------|
| **核心指令区** | 文件开头至首个 `.agents/` 引用之前 | 所有工具**必须**解析 |
| **增强路由区** | `.agents/` 引用、路由表、world.toml 引用 | 支持工具**可以**解析；不支持的工具**忽略** |

此分区确保：不支持 `.agents/` 协议的工具仍可提取核心指令，支持协议的工具可获得完整路由能力。

### 9.3 Mermaid 图表约定

- 流程、架构、关系等可视化内容**推荐**使用 Mermaid 基础语法
- Mermaid 代码块为**辅助说明**，核心约束不得仅存在于图表中
- 使用基础语法，避免自定义样式和高级特性

---

## 10. world.toml Schema

### 10.1 文件位置与格式

- **位置**：`.agents/world.toml`
- **格式**：[TOML v1.0](https://toml.io/en/v1.0.0)
- **编码**：UTF-8
- **约束**：一个 monorepo 仅允许一份 `world.toml`

### 10.2 完整 Schema

```toml
# ═══════════════════════════════════════════
# world.toml — 世界声明式描述
# AgentForge Spec v0.1
# ═══════════════════════════════════════════

# ──── 世界身份 ────
[world]
name = "string"              # 必需：世界标识符（小写 + 连字符）
version = "semver"           # 必需：语义化版本号
description = "string"       # 可选：世界描述
min-alpha = 0.0              # 可选：建议的最低觉醒层级

# ──── 内核声明 ────
[kernel]
# 不可分割的最小世界文件清单
# 路径相对于 .agents/ 目录
manifest = "world.toml"      # 自描述引用
readme = "README.md"         # 世界入口文档

rules = [                    # 内核级规则文件列表
    "rules/context-economy.md",
    "rules/documentation.md",
    "rules/skills.md",
]

references = [               # 内核级参考文档列表
    "docs/references/agent-collaboration-metamodel.md",
]

workflows = [                # 内核级工作流列表
    "workflows/role-review.md",
]

roles_framework = "roles/README.md"  # 角色框架定义

# 不可覆盖的宇宙法则
# 子世界禁止通过同名文件覆盖以下规则名
immutable_rules = ["string"]

[kernel.meta]
self-referential = bool      # manifest 是否递归自指
portable = bool              # kernel 是否可跨项目移植
boundary-policy = "string"   # 边界管理说明所在目录

# ──── 片段声明 ────
# 每个片段是一个领域内聚的可选能力组合
[fragments.<fragment-id>]
version = "semver"           # 片段版本号
includes = ["string"]        # 包含的文件路径列表（相对于 .agents/）
optional = bool              # 是否可选（false = 必装）
description = "string"       # 片段描述

# ──── 能力声明 ────
[capabilities]
skills = "skills/"           # 技能目录路径
scripts_standalone = ["string"]  # 独立脚本路径列表
templates = "templates/"     # 模板目录路径

[capabilities.meta]
portable = bool              # 能力层是否可移植

# ──── 记忆声明 ────
[memory]
paths = ["string"]           # 知识沉淀路径列表
organization = ["string"]    # 组织实体（角色实例、团队）路径列表
portable = bool              # 是否可移植（通常为 false）
versionable = bool           # 是否可版本化
```

### 10.3 字段约束汇总

| 路径 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `world.name` | string | 是 | 小写 + 连字符，全局唯一 |
| `world.version` | string | 是 | 遵循 SemVer 2.0 |
| `world.description` | string | 否 | 人类可读描述 |
| `kernel.rules` | string[] | 是 | 至少包含 1 条内核规则 |
| `kernel.immutable_rules` | string[] | 是 | 可为空数组 |
| `kernel.meta.self-referential` | bool | 否 | 默认 `true` |
| `kernel.meta.portable` | bool | 否 | 默认 `true` |
| `fragments.*.version` | string | 是 | 每个片段必须声明版本 |
| `fragments.*.includes` | string[] | 是 | 至少包含 1 个文件 |
| `fragments.*.optional` | bool | 是 | `false` 表示该片段必装 |
| `capabilities.skills` | string | 否 | 技能目录路径 |
| `memory.portable` | bool | 否 | 默认 `false` |
| `memory.versionable` | bool | 否 | 默认 `false` |

### 10.4 最小 world.toml 示例

```toml
[world]
name = "my-project"
version = "1.0.0"
description = "My project's agent world"

[kernel]
rules = ["rules/context-economy.md"]
immutable_rules = ["context-economy"]

[kernel.meta]
self-referential = true
portable = true
```

---

## 11. .agents/ 标准目录结构

### 11.1 完整目录树（Level 4 全量）

```
.agents/
├── README.md              # 目录说明与导航（推荐）
├── world.toml             # 世界声明（Level 3+）
├── registry.toml          # 注册源配置（可选）
│
├── kernel/                # 内核边界管理元数据（Level 3+）
│   └── README.md
│
├── rules/                 # 领域规则（Level 1+）
│   ├── <rule-id>.md
│   └── ...
│
├── skills/                # 技能目录（Level 2+）
│   └── <skill-name>/
│       ├── SKILL.md       # 必需
│       ├── scripts/
│       ├── tests/
│       ├── schemas/
│       ├── references/
│       └── evals/
│
├── workflows/             # 工作流定义（Level 2+）
│   └── <workflow-id>.md
│
├── scripts/               # 自动化脚本（Level 2+）
│   └── <script>.py|sh
│
├── templates/             # 标准化模板（Level 2+）
│   └── <template>.md
│
├── roles/                 # 角色实例（Level 4）
│   ├── README.md
│   └── <role-name>.md
│
├── teams/                 # 团队实例（Level 4）
│   ├── README.md
│   └── <team-name>.md
│
└── docs/                  # AI 专属知识库（Level 2+）
    ├── README.md
    ├── references/        # 参考文档
    ├── guides/            # 指南
    ├── sources/           # 来源材料
    └── superpowers/       # 长期沉淀归档
        ├── specs/
        ├── plans/
        ├── retrospectives/
        └── memories/
```

### 11.2 各级别最小目录集

| 级别 | 必需文件/目录 |
|------|-------------|
| **Level 0** | `AGENTS.md` |
| **Level 1** | + `.agents/rules/` (至少 1 个规则文件) |
| **Level 2** | + `.agents/skills/` 或 `.agents/workflows/` 或 `.agents/scripts/` (至少 1 个) |
| **Level 3** | + `.agents/world.toml` |
| **Level 4** | + `.agents/roles/` 或 `.agents/teams/` (至少 1 个)，且存在多个 `AGENTS.md` 层级 |

### 11.3 命名规范

| 规则 | 说明 | 示例 |
|------|------|------|
| 目录名 | 小写 + 连字符（复数形式） | `rules/`, `skills/`, `docs/` |
| 规则文件 | 小写 + 连字符 + `.md` | `context-economy.md` |
| 技能目录 | 小写 + 连字符 | `pdf-to-markdown/` |
| 工作流文件 | 小写 + 连字符 + `.md` | `pr-review.md` |
| 脚本文件 | 小写 + 连字符 + 扩展名 | `check_env.py` |
| 角色文件 | 小写 + 连字符 + `.md` | `collaboration-architect.md` |
| 团队文件 | 小写 + 连字符 + `.md` | `core-governance.md` |

### 11.4 人类文档与 AI 文档的物理隔离

```
project-root/
├── README.md              ← 人类 + AI 共享
├── docs/                  ← 面向人类开发者的文档
│   ├── tech/              ← 技术文档（API、集成、部署）
│   └── general/           ← 通用知识
│
├── AGENTS.md              ← AI 入口（人类可读）
└── .agents/
    └── docs/              ← 面向 AI 智能体的知识库
        ├── references/    ← 架构参考、协议定义
        └── superpowers/   ← 归档沉淀
```

**核心原则**：

- `README.md` 与 `docs/` 面向人类开发者
- `.agents/docs/` 面向 AI 智能体
- 两者严禁混入：人类技术文档不放 `.agents/docs/`，AI 参考不放 `docs/`
- 共享知识通过引用关联，而非复制

---

## 12. 兼容性矩阵

### 12.1 与主流工具的兼容性

| 特性 | Codex CLI | Claude Code | Cursor | AgentForge 工具 |
|------|-----------|-------------|--------|----------------|
| 读取 `AGENTS.md` | 是 | 忽略（读 CLAUDE.md） | 忽略 | 是 |
| 解析上下文路由表 | 否（当作普通文本） | 否 | 否 | 是 |
| 读取 `.agents/rules/` | 否 | 否 | 否（有自己的 rules） | 是 |
| 解析 `world.toml` | 否 | 否 | 否 | 是 |
| 世界继承 | 否 | 否 | 否 | 是 |
| 技能 SKILL.md | 否 | 否 | 否 | 是（兼容 agentskills.io） |

### 12.2 降级策略

不识别 AgentForge 增强协议的工具仍可通过以下方式获得价值：

1. **Level 0 完整可用**：`AGENTS.md` 的核心指令区是纯 Markdown，任何工具均可解析
2. **引用可忽略**：`.agents/` 引用对不识别的工具表现为普通链接，不影响主文件阅读
3. **手动桥接**：用户可将 `.agents/rules/` 内容内联到 `AGENTS.md` 中，退化为 Level 0

### 12.3 与其他约定的共存

| 共存文件 | 处理方式 |
|---------|---------|
| `CLAUDE.md` | 可并存；`AGENTS.md` 为全局契约，`CLAUDE.md` 为 Claude 专属补充 |
| `.cursor/rules/` | 可并存；Cursor 规则优先于 Cursor 上下文，`AGENTS.md` 作为工具无关基准 |
| `.github/copilot-instructions.md` | 可并存；Copilot 指令为 Copilot 专属，`AGENTS.md` 为通用契约 |

**推荐做法**：`AGENTS.md` 作为工具无关的"宪法"，各工具专属文件作为"实施细则"。

---

## 13. 附录

### 附录 A：注册源配置（registry.toml）

`registry.toml` 定义世界级别的技能/规则注册源，支持本地和远程注册表：

```toml
# .agents/registry.toml

[registries.local]
url = "../registry-index"    # 本地注册表路径
type = "git"
priority = 1                 # 优先级（数值越小优先级越高）

[registries.default]
url = "https://github.com/agentforge/registry-index"
type = "git"
priority = 2
```

### 附录 B：角色文件模板

```markdown
# [角色名称]

## Role Identity

- **Name**: `<role-id>`
- **Domain**: <领域>
- **Description**: <角色描述>

## Responsibilities

- <职责 1>
- <职责 2>

## Default Bindings

### Rules
- `.agents/rules/<rule>.md`

### References
- `.agents/docs/references/<reference>.md`

### Skills
- `<skill-name>`

## Non-Goals

- <不属于此角色的范围>
```

### 附录 C：版本策略

- **规范版本**：遵循 SemVer 2.0（`MAJOR.MINOR.PATCH`）
- **世界版本**（`world.toml` 中的 `world.version`）：遵循 SemVer 2.0
- **片段版本**（`fragments.*.version`）：遵循 SemVer 2.0
- Kernel 变更必须升级 `world.version` 的至少 `MINOR` 版本

### 附录 D：验证清单

用于自检项目是否符合声明级别的合规性：

#### Level 0 检查

- [ ] `AGENTS.md` 存在于项目根目录
- [ ] 文件编码为 UTF-8
- [ ] 核心指令区为自包含纯 Markdown

#### Level 1 检查

- [ ] `.agents/rules/` 目录存在且至少包含 1 个规则文件
- [ ] `AGENTS.md` 包含上下文路由表
- [ ] 规则文件使用小写 + 连字符命名

#### Level 2 检查

- [ ] `skills/` 或 `workflows/` 或 `scripts/` 至少存在一个
- [ ] 每个技能目录包含 `SKILL.md`
- [ ] `.agents/README.md` 存在

#### Level 3 检查

- [ ] `.agents/world.toml` 存在且格式合法
- [ ] `world.name` 和 `world.version` 已声明
- [ ] `kernel.rules` 至少包含 1 条规则
- [ ] `kernel.immutable_rules` 已声明

#### Level 4 检查

- [ ] 存在多个 `AGENTS.md` 层级
- [ ] `roles/` 或 `teams/` 至少存在一个
- [ ] 子世界覆盖说明已声明（如有覆盖）
- [ ] 嵌套深度 ≤ 3 层

---

> **下一步**：本草案待社区评审后，将提取 JSON Schema 验证工具、CLI 初始化工具（`agentforge init`）与合规检查工具（`agentforge validate`），形成完整的工具链闭环。
