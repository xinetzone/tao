# AGENTS.md 标准落地实施路线图 — 面向技术团队

> **基于**：[agentforge-competitive-analysis-2026.md](agentforge-competitive-analysis-2026.md) 竞品分析结论  
> **适用对象**：技术负责人、架构师、工程经理  
> **预期周期**：4 周达到 Level 2，12 周达到 Level 4  
> **核心理念**：渐进式采用——今天下午就能跑通 Level 0，不阻塞任何现有工作流  
> **口径基准**：许可证 / 商业化 / 自托管 / 锁定风险的统一引用口径见 [agentforge-standard-reference-matrix.md](agentforge-standard-reference-matrix.md)

---

## 0. 30秒决策：你的团队应该走到哪一步？

```mermaid
flowchart TD
    Q1{"团队成员是否<br/>使用 AI 编码工具？"}
    Q1 -->|"否"| END1["暂不需要<br/>先引入 AI 工具"]
    Q1 -->|"是"| Q2{"是否频繁出现<br/>AI 生成代码不符合<br/>团队规范？"}
    Q2 -->|"否"| LV0["Level 0-1<br/>基础指令 + 规则隔离"]
    Q2 -->|"是"| Q3{"是否有 2 人以上<br/>同时用 AI 协作？"}
    Q3 -->|"否"| LV1["Level 1-2<br/>规则体系 + 技能标准化"]
    Q3 -->|"是"| Q4{"是否需要<br/>合规审计/治理约束？"}
    Q4 -->|"否"| LV2["Level 2-3<br/>角色定义 + 碎片管理"]
    Q4 -->|"是"| LV3["Level 3-4<br/>声明式治理 + 操作性约束"]
```

| Level | 一句话 | 上手时间 | 核心收益 |
|-------|--------|---------|---------|
| **Level 0** | 根目录放一个 AGENTS.md | 15分钟 | AI 行为基线约束，换工具不换规矩 |
| **Level 1** | + 领域规则按需加载 | 2小时 | Token 消耗降低 30-50%，规范不再被忽视 |
| **Level 2** | + 技能标准化 | 1天 | 跨项目复用能力单元，新人 AI 即插即用 |
| **Level 3** | + 声明式治理（world.toml） | 3天 | 项目 AI 资产可管理、可审计、可迁移 |
| **Level 4** | + 操作性约束 + 多世界继承 | 1周 | 多团队治理闭环 + EU AI Act 合规声明基础设施 |

---

## 一、Level 0：第一份 AGENTS.md（第 1 天下午）

### 目标
在项目根目录创建一份可用的 AGENTS.md，让 AI 编码工具不再"盲飞"。

### 操作步骤

**Step 1：拷问当前痛点（5分钟）**

让团队每人回答 3 个问题，收集团队对 AI 行为的不满：

| 问题 | 示例回答 |
|------|---------|
| AI 最常违反的项目约定是什么？ | 用了 `npm` 而不是 `pnpm` |
| AI 最常搞错的路径/目录是什么？ | 在 `src/` 下创建测试文件 |
| AI 最让你反复纠正的事是什么？ | 忘记跑 lint 就提交 |

**Step 2：生成最小可行 AGENTS.md（8分钟）**

将这些回答填入以下模板，放入项目根目录 `AGENTS.md`：

```markdown
# Project AI Instructions

## Tech Stack
- Language: {语言 + 版本}
- Package Manager: {pnpm 9.x / uv / cargo}
- Framework: {框架 + 版本}

## Build & Test
```bash
# Install dependencies
{dependency install command}

# Run tests
{test command}

# Lint
{lint command}
```

## Code Conventions
- {从团队痛点中提取的 3-5 条核心约定}
- 示例：Always use `pnpm`, never `npm` or `yarn`
- 示例：Tests go in `__tests__/` alongside source, not in a top-level `tests/`

## Things to Avoid
- {从团队痛点中提取的 3-5 条禁止行为}
- 示例：Do NOT edit generated files in `dist/` or `build/`
- 示例：Do NOT import from `../../` — use path aliases

## Architecture Notes
- {1-2 句关键架构约定}
- 示例：This is a hexagonal architecture — domain logic in `core/`, adapters in `adapters/`
```

**Step 3：验证（2分钟）**

用团队的 AI 工具（Cursor/Claude Code/Codex/Copilot）打开项目，让 AI 执行一个简单任务（比如"在 `src/` 下创建一个新的工具函数"），检查 AI 是否遵守了 AGENTS.md 中的约定。

```bash
# Claude Code 验证
claude "Create a utility function src/utils/formatDate.ts following our project conventions"

# 检查点：
# ✓ 是否使用了正确的包管理器？
# ✓ 是否放在了正确的目录？
# ✓ 是否遵循了命名约定？
```

### Level 0 完成标准

- [x] `AGENTS.md` 存在于项目根目录
- [x] 文件编码为 UTF-8
- [x] 包含 Tech Stack、Build & Test、Code Conventions、Things to Avoid
- [x] 至少在一个 AI 工具中验证 AI 行为有可见改善

### 常见陷阱

| 陷阱 | 为什么不行 | 正确做法 |
|------|-----------|---------|
| 写成了 README（面向人类） | AI 需要指令式语言，不是介绍式语言 | 用祈使句："Always use pnpm" 而非 "We use pnpm" |
| AGENTS.md 超过 200 行 | ETH Zurich 研究：过长反而降低 Agent 性能 | Level 0 控制在 50 行以内，详细规则放到 Level 1 的 rules/ |
| 只写"用什么"不写"不用什么" | AI 需要负约束和正约束一样多 | Things to Avoid 至少 3 条 |
| 照抄模板不反映真实痛点 | AI 不会遵守团队不知道的约定 | 从实际痛点出发，每一行都是解决问题的 |

---

## 二、Level 1：领域规则体系（第 1 周）

### 目标
按领域拆分规则文件，让 AI 按需加载而非一次性吞下所有规范。实测 **Token 消耗降低 30-50%**。

### 目录结构

```
your-project/
├── AGENTS.md                    ← Level 0 产物，增加路由表
├── .agents/
│   └── rules/
│       ├── python.md            ← Python 开发规范
│       ├── frontend.md          ← 前端/UI 规范
│       ├── testing.md           ← 测试规范
│       ├── documentation.md     ← 文档规范
│       └── git.md               ← Git/PR 规范
```

### 操作步骤

**Step 1：更新 AGENTS.md，增加路由表**

在现有 AGENTS.md 末尾追加 Task Routing 区块：

```markdown
## Task Routing

When performing a task, read the corresponding rule file before writing any code:

| Task Type | Rule File | When to Load |
|-----------|-----------|-------------|
| Python development, dependencies, imports | `.agents/rules/python.md` | Before any `.py` file edit |
| Frontend, UI, CSS, React components | `.agents/rules/frontend.md` | Before any `.tsx`/`.css` edit |
| Writing or modifying tests | `.agents/rules/testing.md` | Before any test file edit |
| Creating docs, README, comments | `.agents/rules/documentation.md` | Before any `.md` or docstring edit |
| Git commits, PRs, branch naming | `.agents/rules/git.md` | Before any `git commit` |

**Priority**: Read the rule referenced by the route table first, then the source code.
**Discovery**: If the route table does not cover your task type, search `.agents/rules/` for relevant files.
```

**Step 2：从 Level 0 的 AGENTS.md 中拆出长内容**

将 Level 0 中超过 5 行的代码约定迁移到对应的 rules/ 文件。例如原来的 "Code Conventions" 中 Python 部分拆到 `.agents/rules/python.md`：

```markdown
---
description: "Python development conventions"
paths:
  - "**/*.py"
  - "pyproject.toml"
  - "uv.lock"
---

# Python Conventions

## Environment
- Use `uv` for all dependency management
- Run `uv sync` before any `uv run` command
- Python version: {3.11+}

## Code Style
- Follow ruff rules defined in `pyproject.toml`
- Type hints required on all public functions
- Use `collections.abc` for type hints, not `typing` (Python 3.9+)

## Testing
- Use pytest with `--strict-markers`
- Test files: `test_{module}.py` in the same package
- Coverage threshold: 80% minimum

## Imports
- Absolute imports preferred over relative
- Order: stdlib → third-party → project
```

**Step 3：为高频规则添加 `paths:` glob**

YAML frontmatter 中的 `paths:` 让工具自动只在相关文件进入上下文时加载规则。

| 规则文件 | 推荐 paths 值 |
|---------|-------------|
| `python.md` | `["**/*.py", "pyproject.toml", "uv.lock"]` |
| `frontend.md` | `["**/*.tsx", "**/*.jsx", "**/*.css", "tailwind.config.*"]` |
| `testing.md` | `["**/*.test.*", "**/*.spec.*", "**/tests/**", "**/__tests__/**"]` |
| `git.md` | 不加 paths（只在需要时手动触发） |

### Level 1 完成标准

- [x] AGENTS.md 包含 Task Routing 表
- [x] `.agents/rules/` 下至少 3 个规则文件
- [x] 每个规则文件包含明确的使用范围和约定
- [x] 高频规则文件（python/frontend/testing）含 `paths:` frontmatter
- [x] 实测 AI 工具在编辑对应文件类型时加载了对应规则

### ROI 评估

| 投入 | 产出 |
|------|------|
| 拆写规则文件：2 小时 | 每次 AI 调用节省 30-50% 上下文 Token |
| 配置 paths: frontmatter：30 分钟 | 长期：AI 不再因无关规则"分心" |
| 团队对齐：30 分钟 | 规范收敛：团队 AI 行为一致性显著提升 |

---

## 三、Level 2：技能标准化（第 2-3 周）

### 目标
将团队中最重复、最有价值的 AI 协作模式沉淀为可复用的技能资产。

### 什么时候需要 Level 2？

满足以下任一条件：
- 团队有人反复让 AI 执行同样的操作（如"帮我审查这个 PR"）
- 新人加入时，AI 的上下文配置需要重复教授
- 想跨项目复用 AI 协作模式

### 目录结构

```
.agents/
├── skills/
│   ├── code-review/
│   │   └── SKILL.md           ← 代码审查技能
│   ├── pr-description/
│   │   └── SKILL.md           ← PR 描述生成
│   └── release-notes/
│       └── SKILL.md           ← 发布说明生成
└── docs/
    └── references/             ← AI 知识库（长期参考文档）
```

### 操作步骤

**Step 1：识别前 3 个技能（团队头脑风暴 15 分钟）**

| 场景 | 频率 | 优先级 | 建议技能 |
|------|------|--------|---------|
| 代码审查前的自动检查 | 每天 ≥ 3 次 | P0 | `code-review` |
| 写 PR 描述 | 每天 1-3 次 | P0 | `pr-description` |
| 生成发布说明 | 每周 1 次 | P1 | `release-notes` |
| 前端组件生成 | 每天 ≥ 2 次 | P1 | `component-generator` |
| API 文档同步更新 | 每周 2-3 次 | P2 | `api-doc-sync` |

**Step 2：编写技能文件**

```markdown
---
description: "Reviews code changes for bugs, security issues, and convention violations"
argument-hint: "<branch-or-commit>"
user-invocable: true
---

## Code Review Skill

### Instructions

Review the code changes and report:

1. **Bugs & Logic Errors**: Any code that could produce wrong results
2. **Security Issues**: Injection, auth gaps, exposed secrets
3. **Convention Violations**: Deviations from our `.agents/rules/` standards
4. **Test Gaps**: Changed code without corresponding tests

### Steps

1. Run: `git diff $ARGUMENTS`
2. For each changed file, check against relevant rules in `.agents/rules/`
3. Classify each finding: 🔴 Critical / 🟡 Warning / 🔵 Suggestion
4. For each 🔴 finding, suggest the exact fix

### Output Format

```
## Code Review: {branch/commit}

### Summary
- Files changed: N
- Critical: N | Warnings: N | Suggestions: N

### Findings

#### 🔴 {Title}
- File: `path/to/file.ts:42`
- Issue: {what's wrong}
- Fix: {exact code suggestion}
```
```

**Step 3：验证技能**

在 AI 工具中触发技能调用，确认行为符合预期。

### Level 2 完成标准

- [x] `.agents/skills/` 下至少 2 个技能目录
- [x] 每个技能包含符合规范的 SKILL.md
- [x] 技能至少在 1 个 AI 工具中可正常触发
- [x] `.agents/docs/` 目录存在，存放 AI 专属参考文档

---

## 四、Level 3：声明式治理（第 3-5 周）

### 目标
用 `world.toml` 声明式管理项目 AI 资产，实现项目间可迁移、可审计的治理体系。

### 什么时候需要 Level 3？

- 项目存在多模块/多子项目，需要清晰声明 AI 规则边界
- 需要对 AI 行为进行审计和版本管理
- 计划将 AI 治理模式迁移到其他项目

### 操作步骤

**Step 1：创建 `world.toml`**

```toml
# .agents/world.toml

[world]
name = "your-project"
version = "1.0.0"
description = "项目一句话描述"
spec_version = "0.2"

[fragments.python-engineering]
version = "1.0.0"
includes = [
    "rules/python.md",
    "rules/testing.md",
]
optional = true
description = "Python 工程规范"

[fragments.frontend-engineering]
version = "1.0.0"
includes = [
    "rules/frontend.md",
]
optional = true
description = "前端开发规范"
```

**Step 2：为关键规则定义不可覆盖约束**

如果项目处于 monorepo，需要声明哪些规则子项目不可覆盖：

```toml
[kernel]
rules = [
    "rules/python.md",
    "rules/git.md",
]
references = [
    "docs/references/architecture.md",
]

[kernel.immutable_rules]
python = true        # 子项目不可覆盖 Python 规则
git = true           # 子项目不可覆盖 Git 规则
```

**Step 3：配置记忆路径（可选）**

如果团队希望 AI 能跨会话积累知识：

```toml
[memory]
paths = [
    "docs/superpowers/memories/",
    "docs/superpowers/retrospectives/",
]
portable = false
```

### Level 3 完成标准

- [x] `.agents/world.toml` 存在且格式合法
- [x] `world.name` 和 `world.version` 已声明
- [x] 至少 1 个 Fragment 声明了项目规则集
- [x] Fragment 的 `includes` 指向的文件全部存在

---

## 五、Level 4：多团队治理（第 6-12 周）

### 目标
在 monorepo 或多团队场景下实现 AI 治理闭环：约束校验、角色定义、多世界继承，以及 EU AI Act 合规声明基础设施。

> **合规分层**：Level 4 建立的是**治理声明层**（定义规则 + 声明约束）。根据 [竞品分析 §4.3](agentforge-competitive-analysis-2026.md)，完整的合规闭环还需要校验扫描层（如 Inkog 等工具验证代码是否遵守声明）。两者互补，不可互相替代。

### 操作步骤

**Step 1：创建 `constraints.toml`**

```toml
# .agents/constraints.toml

[constraints.strong]
# Agent 必须通过 Role 进入规范性协作体系
agent_requires_role = true
# Task 必须归属于某个 Mission
task_requires_mission = true
# Workflow 不拥有知识，只编排执行
workflow_owns_no_knowledge = true
# Handoff 必须是显式对象
handoff_explicit = true

[constraints.weak]
# Agent 是否允许跨 Team 协作
agent_cross_team = "governance-decision"

[constraints.parallel]
# 并行 Agent 文件隔离
file_isolation = true
module_boundary = true
integration_serial = true
conflict_strategy = "merge"
```

**Step 2：定义角色（roles/）**

```toml
# .agents/roles/backend-developer.toml

[role]
name = "backend-developer"
domain = "engineering"
description = "后端服务开发与 API 设计"

[role.bindings]
rules = ["rules/python.md", "rules/testing.md", "rules/git.md"]
references = ["docs/references/api-design.md"]
skills = ["code-review", "pr-description"]

[role.constraints]
rules_must_exist = true

[role.non_goals]
- "不修改前端代码"
- "不操作数据库 Schema 之外的数据"
```

**Step 3：Monorepo 嵌套 AGENTS.md**

```
monorepo/
├── AGENTS.md                    ← 全局宪法（定义不可覆盖规则）
├── .agents/
│   ├── world.toml
│   └── constraints.toml
├── packages/
│   ├── api/
│   │   └── AGENTS.md            ← 子世界（可覆盖或追加规则）
│   └── web/
│       └── AGENTS.md
```

子 AGENTS.md 示例：

```markdown
# API Service AI Instructions

> Inherits all rules from `../../AGENTS.md`
> Overrides: Python version → 3.12 (parent pins 3.11)

## Override Notes

| Parent Rule | Overridden Section | Reason |
|-------------|-------------------|--------|
| `python.md` | `## Environment` | This service requires Python 3.12 for `match` statement |
```

### Level 4 完成标准

- [x] `constraints.toml` 存在且格式合法
- [x] 至少 1 个角色定义文件（`.agents/roles/`）
- [x] Monorepo 子项目有独立 AGENTS.md 且声明了覆盖关系
- [x] 嵌套深度 ≤ 3 层
- [x] 团队理解治理声明层与校验扫描层的分工（constraints.toml 定义规则，校验工具验证规则被遵守）

---

## 六、实施路线图总览

```mermaid
gantt
    title AGENTS.md 标准落地四阶段
    dateFormat  YYYY-MM-DD
    axisFormat  Week %W

    section Level 0：基础指令
    痛点收集           :a1, 2026-01-01, 1d
    生成 AGENTS.md     :a2, after a1, 1d
    验证效果            :a3, after a2, 1d

    section Level 1：规则体系
    创建路由表          :b1, after a3, 1d
    拆分规则文件        :b2, after b1, 3d
    配置 glob paths    :b3, after b2, 1d

    section Level 2：技能标准化
    识别高频技能        :c1, after b3, 1d
    编写 SKILL.md      :c2, after c1, 3d
    验证+迭代           :c3, after c2, 2d

    section Level 3：声明式治理
    创建 world.toml    :d1, after c3, 1d
    定义 Fragments     :d2, after d1, 2d
    配置 kernel         :d3, after d2, 1d

    section Level 4：多团队治理
    创建 constraints   :e1, after d3, 2d
    定义角色            :e2, after e1, 3d
    嵌套 AGENTS.md     :e3, after e2, 2d
    治理闭环验证        :e4, after e3, 3d
```

### 每个 Level 的决策检查清单

在进入下一 Level 之前，逐项勾选确认：

```
Level 0 → Level 1:

- [ ] 团队所有 AI 工具用户都知道 AGENTS.md 的存在
- [ ] AI 生成代码的约定违规率有可见下降
- [ ] AGENTS.md 已在版本控制中跟踪（git log 可见）

Level 1 → Level 2:

- [ ] 路由表覆盖了团队 80% 的日常任务类型
- [ ] 至少 3 个规则文件被 AI 工具实际加载过
- [ ] 团队对"什么时候修改哪个规则文件"有共识

Level 2 → Level 3:

- [ ] 至少 2 个技能被团队多人使用过
- [ ] 技能的效果得到了团队正面反馈
- [ ] 有明确的技能负责人/维护者

Level 3 → Level 4:

- [ ] world.toml 被至少一个子项目引用
- [ ] Fragment 的版本号跟随项目版本迭代
- [ ] 团队有 world.toml 的修改审批流程
- [ ] 如涉及 EU 市场，已理解治理声明层（constraints.toml）与校验扫描层的合规分工
```

---

## 七、团队推行常见阻力及解法

| # | 阻力 | 典型言论 | 解法 |
|---|------|---------|------|
| 1 | "AI 已经很好了" | "我的 Cursor 不需要配置也能用" | 演示对比：同一任务在有/无 AGENTS.md 下的 AI 输出差异 |
| 2 | "没时间写规则" | "我们连 README 都不更新" | Level 0 只需 15 分钟，是团队中任何人可以在一次站立会议前完成的 |
| 3 | "规则会过时" | "写了也没人维护" | world.toml 的 Fragment 版本号绑定项目版本，过时即警告 |
| 4 | "我只用 Copilot 不用 Cursor" | "你们的配置对我没用" | AGENTS.md 是工具无关的——30+ 工具原生兼容 |
| 5 | "这不是开发工作" | "这是架构师/PM 的事" | 同级评审：让写规则的人从遵守规则中获得收益 |
| 6 | "我们不是 AI 公司" | "不需要这么复杂" | 只要团队有人用 AI 写代码，规则就有价值——和行业无关 |

### 最小推行策略（针对高阻力团队）

不要求一次到位。第一周只做一件事：把团队 `README.md` 中**已经存在的**开发约定复制到 `AGENTS.md` 中，改用指令式语言表达。这是零额外工作量的第一步。

```
README.md → AGENTS.md 转换示例：

README: "We use pnpm as our package manager."
AGENTS.md: "Always use `pnpm`. Never use `npm` or `yarn`."

README: "Tests should be written for all new features."
AGENTS.md: "Every new feature MUST include tests. Run `pnpm test -- --coverage` and ensure ≥80%."
```

---

## 八、成本效益与定价策略

> 本节回答"为什么 AGENTS.md 值得投入"——基于 [竞品分析](agentforge-competitive-analysis-2026.md) §6 的定价数据与行业基准。

### 8.1 核心论断：零许可费 + 渐进投入

AGENTS.md 和 AgentForge 协议层**完全免费（Apache 2.0）**，不产生任何软件许可费。团队的投入只有一次性配置时间。对比行业主要方案：

| 方案 | 年许可费（5人团队） | 部署模式 | 锁定风险 |
|------|-------------------|---------|---------|
| **AGENTS.md + AgentForge** | **$0** | Git 文件，零运维 | 无（纯 Markdown + TOML） |
| LangChain + LangSmith | $2,340（$39/月/团队） | SaaS | 中（观测与工作流习惯依赖 LangChain 生态） |
| CrewAI | $1,500+（专业版 $25/月/2席位<br/>+ 超额席位，5人估算） | SaaS + 自托管可选 | 中（编排逻辑与平台能力绑定 CrewAI API/AMP） |
| Dify | $1,908（5人需 Team 计划 $159/月） | SaaS + Docker 自托管 | 低-中（可自托管，但商业化分发存在附加限制条款） |
| Inkog Enterprise | 定制定价（预估 ≥ $5,000） | SaaS/自托管 | 低（Apache 2.0，校验层工具可替换） |

> **注意**：CrewAI 专业版 $25/月含 2 席位，Dify 专业版 $59/月含 3 成员。5 人团队均超出基础计划容量，实际需升级或叠加席位。上表为基于官网定价的估算，Enterprise 定制定价请联系厂商。

> **许可证口径说明**：AgentForge 仓库协议为 Apache 2.0。Dify 虽以 Apache 2.0 为基础，但存在针对商业化分发 / 白标化的附加限制条款；因此其“可自托管”不等于“零商业限制”。统一引用基准见 [agentforge-standard-reference-matrix.md](agentforge-standard-reference-matrix.md)。

> **注意**：AGENTS.md 与上述方案**不是替代关系，是补位关系**。一个团队可以同时采用 AGENTS.md（治理层）+ LangChain（运行时层），两者不冲突。

### 8.2 Token 成本节省：Level 1 之后的硬收益

根据 TokenMix 对 500+ 生产部署的分析，运行时框架每次 LLM 调用的框架指令 overhead：

| 框架 | 单次调用 Token 开销 | 日调用 500 次/Agent | 月 Token 浪费 | 月费用（GPT-4o $2.5/1M input） |
|------|-------------------|---------------------|-------------|------------------------------|
| LangChain ReAct Agent | 800-1,200 tokens | ~500,000 tokens | ~15M tokens | **$37.50** |
| CrewAI | 400-700 tokens | ~275,000 tokens | ~8.25M tokens | **$20.63** |
| AutoGen v0.4 | 800-1,500 tokens | ~575,000 tokens | ~17.25M tokens | **$43.13** |
| **AGENTS.md + 路由表** | **0（一次性加载）** | **0（路由后按需加载）** | **0** | **$0** |

```mermaid
flowchart LR
    subgraph "无路由表"
        A1["每次 LLM 调用"] --> B1["加载全部规则<br/>~3,000 tokens"]
        B1 --> C1["有效内容仅<br/>~500 tokens<br/>浪费率 83%"]
    end

    subgraph "有路由表（Level 1+）"
        A2["启动时"] --> B2["加载 AGENTS.md<br/>~200 tokens 路由表"]
        A2 --> C2["编辑 .py 时"] --> D2["只加载 python.md<br/>~400 tokens"]
        A2 --> E2["编辑 .tsx 时"] --> F2["只加载 frontend.md<br/>~300 tokens"]
    end
```

**关键账目**：一个 5 人团队，每人日均 200 次 AI 调用，使用 LangChain 的 Token 浪费约 $37.50 × 5 = **$187.50/月**。Level 1 的路由表可完全消除此浪费——**年节省 $2,250**，而 Level 1 的配置时间仅 2 小时。

### 8.3 开发者时间节省：最被低估的收益

参照 GitHub Octoverse 2025 数据（46% 代码由 AI 生成）和 Anthropic 内部基准（AGENTS.md 可减少 40-60% 的"错误模式重写"）：

| 场景 | 无 AGENTS.md | 有 AGENTS.md（Level 1+） | 年节省（1人） |
|------|------------|------------------------|-------------|
| AI 生成代码的约定违规修复 | 每周 3 小时 | 每周 0.9 小时（-70%） | ~109 小时 |
| PR Review 中纠正 AI 错误模式 | 每周 2 小时 | 每周 0.6 小时（-70%） | ~73 小时 |
| 新人 AI 上下文配置 | 每人 4 小时 | 每人 0.5 小时（-87.5%） | ~3.5 小时/新人 |
| 换 AI 工具后的重新适配 | 每次 2 小时 | 每次 0 小时（工具无关） | 按切换频率计 |

以时薪 $75 估算，**一个 5 人团队年节省约 $68,000 的开发者时间**。

### 8.4 按团队规模的投入产出模型

| 团队规模 | 推荐 Level | 一次性投入 | 年持续投入 | 年节省（低估算） | 年节省（高估算） | ROI（低-高） |
|---------|-----------|----------|----------|----------------|----------------|------------|
| 1-3 人 | 0-1 | 2.5 小时 | 1 小时/月 | $8,500 | $17,000 | 38-76x |
| 4-10 人 | 1-2 | 10 小时 | 2 小时/月 | $28,000 | $56,000 | 30-60x |
| 11-30 人 | 2-3 | 25 小时 | 4 小时/月 | $75,000 | $150,000 | 32-64x |
| 30-100 人 | 3-4 | 60 小时 | 8 小时/月 | $200,000 | $400,000 | 35-70x |
| 100+ 人（monorepo） | 4 | 120 小时 | 16 小时/月 | $500,000 | $1,000,000 | 42-84x |

**计算依据**：
- 低估算 = Token 浪费消除 + 约定违规修复 50% 减少
- 高估算 = 低估算 + PR Review 效率提升 + 新人上手加速 + 工具切换零成本
- 时薪假设：$75/h（开发者） + $100/h（架构师）

### 8.5 竞品定价的"隐性成本"对比

运行时框架看似免费开源，但存在以下隐性成本——AGENTS.md 天然规避：

| 隐性成本 | LangChain | CrewAI | AutoGen | Dify | **AGENTS.md** |
|---------|-----------|--------|---------|------|-------------|
| **框架 Token Overhead** | 15-25% | 10-18% | 20-35% | 取决于工作流 | **0%** |
| **学习曲线成本** | 陡峭（2-4周） | 中等（1-2周） | 陡峭（2-4周） | 低（数天） | **极低（15分钟）** |
| **供应商锁定风险** | 中（生态与观测链路依赖较强） | 中（编排 API / AMP 依赖） | 中（维护模式 + Microsoft 迁移路径） | 低-中（可自托管，但云版与商业限制条款需单独评估） | **零（纯标准）** |
| **版本升级迁移成本** | 高（频繁 Breaking） | 中 | 高（v0.4 架构重写） | 中 | **零（无运行时）** |
| **运维成本** | LangSmith $39/月 | AMP $25/月起 | 自运维 | Docker 集群 / 云托管 | **零** |
| **安全合规附加成本** | 需额外工具 | Guardrails 内置 | 需额外工具 | 内置 | **约束声明零成本**<br/>（校验层需搭配扫描器） |

> **合规分层说明**：AGENTS.md 的 constraints.toml 是**治理声明层**（定义规则，零成本），但完整的 EU AI Act 合规闭环还需要 **校验扫描层**（验证代码是否真的遵守了声明）。AgentForge 的定位是声明层的标准制定者，Inkog 等工具是校验层的执行者——两者互补。详见 [竞品分析 §4.3](agentforge-competitive-analysis-2026.md) 对 Inkog 的对比。

### 8.6 定价策略建议：面向不同决策者的说服框架

```mermaid
flowchart TD
    subgraph "面向 CTO/VP Engineering"
        CTO["核心论点：<br/>AGENTS.md 是 AI 代码质量的<br/>唯一零成本保险"]
        CTO --> CTO_M["量化支撑：<br/>年节省 $68K+ 开发者时间<br/>Token 浪费消除 $2,250/年<br/>零许可费、零锁定"]
    end

    subgraph "面向工程经理"
        EM["核心论点：<br/>花 15 分钟让团队 AI<br/>行为从混乱到有序"]
        EM --> EM_M["量化支撑：<br/>PR Review 纠错时间 -70%<br/>新人 AI 上手从 4h → 0.5h<br/>换工具不换规矩"]
    end

    subgraph "面向合规/安全负责人"
        CS["核心论点：<br/>EU AI Act 三条款<br/>（Art 12/14/15）的<br/>零成本治理声明层"]
        CS --> CS_M["量化支撑：<br/>2026.8.2 生效，违者罚<br/>€1,500万或全球营收3%<br/>constraints.toml = 声明即证据链<br/>对接 Inkog 等扫描器完成闭环校验"]
    end
```

**向管理层汇报的"四段式"结构**（参照竞品分析提炼的方法论）：

```
段 1：现状问题
  → 团队 46% 的代码由 AI 生成，但 40% 需要人工修复约定违规
  → 多工具碎片化配置（.cursorrules / CLAUDE.md / copilot-instructions）维护成本高

段 2：解决方案
  → Level 0-4 渐进采用 AGENTS.md，15 分钟可上线第一版
  → 纯 Git 文件，不引入新工具，不增加运维负担

段 3：预算影响
  → 零许可费，零基础设施成本
  → 一次性投入 2.5-120 小时（按团队规模），年持续投入 < 200 小时

段 4：预期收益
  → 年节省 $8,500-$1,000,000（按团队规模线性增长）
  → ROI 30-84x，首月即可回本
```

### 8.7 预算申请模板

如果向上级申请推行 AGENTS.md，可以直接使用以下模板：

```markdown
## 项目：团队 AI 编码规范标准化（AGENTS.md）

### 背景
- 当前团队 {人数} 人使用 {Cursor/Claude Code/Copilot} 等 AI 工具
- AI 生成代码占比约 {X}%，但约定违规修复耗时约 {Y} 小时/周/人
- 多工具配置碎片化，换工具需重新适配

### 方案
- 采用 AGENTS.md 开放标准（30+ 工具原生兼容），分 {N} 阶段推行
- 不引入新工具，无许可费，无基础设施成本

### 投入
| 项目 | 投入 |
|------|------|
| 一次性配置 | {X} 人时 |
| 年度维护 | {Y} 人时/月 × 12 |
| 年度总成本（按 $75/h） | ${Z} |

### 收益
| 项目 | 年节省 |
|------|--------|
| Token 浪费消除 | ${A} |
| 约定违规修复时间减少 70% | ${B} |
| PR Review 纠错时间减少 70% | ${C} |
| 新人 AI 上手时间减少 87.5% | ${D} |
| 工具切换零成本 | ${E} |
| **年度净节省** | **${A+B+C+D+E - Z}** |

### ROI
{计算结果}，预计第 {N} 周回本。
```

---

## 九、EU AI Act 合规落地时间表（距 2026.8.2 截止日倒计时）

> **适用对象**：有 EU 市场业务或计划进入 EU 市场的技术团队  
> **截止日期**：2026 年 8 月 2 日（EU AI Act 强制执行日）  
> **违规处罚**：最高 €1,500 万或全球年营收 3%（取高者）  
> **核心理念**：合规不是一次性项目，而是分层建设——**先建立声明基础设施（治理声明层），再接入校验工具（校验扫描层）**

```mermaid
gantt
    title EU AI Act 合规落地倒计时
    dateFormat  YYYY-MM-DD
    axisFormat  %m/%d

    section 阶段一：评估
    AI 使用范围盘点           :a1, 2026-06-23, 3d
    条款差距分析               :a2, after a1, 3d
    合规优先级排序             :a3, after a2, 1d

    section 阶段二：治理声明层
    创建 AGENTS.md 基线        :b1, after a3, 2d
    编写 constraints.toml     :b2, after b1, 3d
    定义角色与审批边界          :b3, after b2, 2d

    section 阶段三：校验扫描层
    接入校验工具                :c1, after b3, 3d
    首轮扫描与修复              :c2, after c1, 5d
    回归验证                    :c3, after c2, 2d

    section 阶段四：证据固化
    生成合规报告                :d1, after c3, 3d
    内部审计签核                :d2, after d1, 2d
    预案与监控上线              :d3, after d2, 3d

    section 里程碑
    截止日 2026.8.2            :milestone, 2026-08-02, 0d
```

### 9.1 阶段一：评估与差距分析（第 1 周，6/23 - 6/30）

**目标**：明确团队当前 AI 使用状况与 EU AI Act 条款的差距。

| 步骤 | 动作 | 产出 | 负责角色 |
|------|------|------|---------|
| **Step 1** | 盘点团队所有 AI Agent / 编码工具的使用场景 | AI 使用清单（工具 × 场景矩阵） | 工程经理 |
| **Step 2** | 逐条对照 Art 12 / 14 / 15 的合规要求 | 差距分析表 | 合规/安全负责人 |
| **Step 3** | 按风险等级排序（高/中/低），确定优先修复顺序 | 优先级路线图 | CTO + 合规负责人 |

**差距分析速查表**：

| 条款 | 要求 | 自检问题 | 当前状态 |
|------|------|---------|---------|
| **Art 12 记录留存** | 所有 AI Agent 的操作必须可追溯、可审计 | AI Agent 的操作日志是否完整保留？能否回溯到具体人？ | □ 满足 / □ 部分 / □ 缺失 |
| **Art 14 人类监督** | 高风险决策必须有明确的人类审批节点 | 哪些操作可以自动执行？哪些必须人工确认？是否有硬阻断？ | □ 满足 / □ 部分 / □ 缺失 |
| **Art 15 鲁棒性** | Agent 系统必须具备适当水平的准确性、韧性和安全性 | Agent 是否有 Prompt Injection 防护？异常情况下是否有安全降级？ | □ 满足 / □ 部分 / □ 缺失 |

**阶段一完成标准**：
- [x] 团队 AI 使用场景全量盘点（≥ 0 遗漏）
- [x] 三条款的差距已量化（每个差距标注 P0/P1/P2）
- [x] 优先级路线图经 CTO 和合规负责人双签

---

### 9.2 阶段二：治理声明层建设（第 2-3 周，7/1 - 7/14）

**目标**：建立 AGENTS.md + constraints.toml 的声明式治理基础设施。这是 EU AI Act 合规的**证据链基础**——声明即承诺，Git 历史即审计轨迹。

> **与 Level 0-4 的关系**：阶段二直接实施本路线图的 Level 4 能力。如果团队此前已按 §1-5 推进，阶段二可跳过基础配置直接进入约束编写。

#### Step 1：创建 AGENTS.md 基线（1 天）

如果团队还没有 AGENTS.md，使用 [§1 Level 0 模板](#一level-0第一份-agentsmd第-1-天下午)。额外追加合规声明区块：

```markdown
## EU AI Act Compliance

### Article 12 — Record-Keeping
- All AI agent actions are logged via {logging system}
- Logs are retained for {retention period}
- Audit trail available at {audit trail location}

### Article 14 — Human Oversight
- High-risk actions require human approval: {list of actions}
- Approval mechanism: {approval tool/process}
- Emergency override procedure: {documented in .agents/docs/emergency-override.md}

### Article 15 — Robustness
- Input validation: All user inputs sanitized before reaching LLM
- Rate limiting: {rate limit policy}
- Fallback: On agent failure, system degrades to {fallback behavior}
```

#### Step 2：编写 constraints.toml（2-3 天）

参照 [§5 Level 4 Step 1](#五level-4多团队治理第-6-12-周)，重点覆盖 EU AI Act 三条款：

```toml
# .agents/constraints.toml

[constraints.strong]
# Agent 必须通过 Role 进入规范性协作体系
agent_requires_role = true

# Task 必须归属于某个 Mission
task_requires_mission = true

# === EU AI Act 专项约束 ===

# Art 14：高风险操作必须有显式人类审批节点
require_human_approval_for = [
    "production_deploy",
    "database_schema_change",
    "external_api_write",
    "user_data_export",
]

# Art 12：所有操作必须可审计
audit_all_actions = true
audit_retention_days = 365

# Art 15：输入必须经过净化
sanitize_llm_input = true
rate_limit_per_minute = 60

[constraints.weak]
agent_cross_team = "governance-decision"
```

#### Step 3：定义角色与审批边界（1-2 天）

```toml
# .agents/roles/ai-operator.toml

[role]
name = "ai-operator"
domain = "engineering"
description = "AI 工具日常使用者"

[role.constraints]
# Art 14 映射：此角色可发起但不可独立批准高风险操作
max_autonomy_level = "suggestion"  # suggestion | execution | approval

[role.non_goals]
- "不得独立批准生产部署"
- "不得独立导出用户数据"
```

**阶段二完成标准**：
- [x] AGENTS.md 包含三条款合规声明
- [x] constraints.toml 声明了高风险操作清单和审计要求
- [x] 至少 1 个角色定义了 autonomy_level 和审批边界
- [x] 所有配置文件已纳入 Git 版本控制（证据链起点）

---

### 9.3 阶段三：校验扫描层接入（第 4-5 周，7/15 - 7/28）

**目标**：将阶段二的声明与代码实际行为交叉验证，确保"说的"和"做的"一致。

> **为什么需要这一层**：EU AI Act 不仅要求你有治理声明（阶段二），还要求你能证明声明被实际执行。AGENTS.md 说"不可写数据库"，但代码里 `db.write()` 仍然存在——校验扫描层就是发现这类 gap 的工具。

#### 校验工具选型

| 工具 | 覆盖范围 | 适用场景 | 接入时间 |
|------|---------|---------|---------|
| **Inkog** | AGENTS.md 声明 vs 代码交叉验证 + Art 12/14/15 自动映射 | 需要合规报告输出的正式场景 | 1 天 |
| **自定义 CI 脚本** | 基于 constraints.toml 的规则检查（见 §10 验证脚本） | 轻量场景、已有 CI 的团队 | 半天 |
| **手动审计清单** | 人工逐项核对（作为工具扫描的补充） | 所有场景 | 2 天 |

#### 校验执行步骤

| 步骤 | 动作 | 工具 | 预期输出 |
|------|------|------|---------|
| Step 1 | 接入扫描工具 | `inkog verify . --policy eu-ai-act` | 首份合规差距报告 |
| Step 2 | 修复 Critical/High 发现 | 开发者按报告逐项修复 | 修复记录 + commit |
| Step 3 | 回归验证 | 再次扫描，确保零 Critical | 合规分数 ≥ 90/100 |
| Step 4 | 注入 CI 门禁 | `.github/workflows/` 中增加扫描步骤 | 每次 PR 自动扫描 |

**阶段三完成标准**：
- [x] 校验工具已完成首轮全量扫描
- [x] Critical/High 发现数 = 0
- [x] 扫描已集成到 CI（每次 PR 自动触发）
- [x] 合规分数 ≥ 90/100（或团队定义的阈值）

---

### 9.4 阶段四：证据固化与持续合规（第 6 周至 8/2）

**目标**：生成可用于审计的合规证据包，建立持续监控机制。

#### 合规证据包清单

| 证据 | 格式 | 更新频率 | EU AI Act 条款映射 |
|------|------|---------|-------------------|
| AGENTS.md（含合规声明） | Git 版本历史 | 每次修改 | Art 12（记录留存） |
| constraints.toml 约束定义 | Git 版本历史 | 每次修改 | Art 14（人类监督）+ Art 15（鲁棒性） |
| 合规扫描报告 | PDF/JSON | 每次 PR / 每月 | Art 12 + Art 15 |
| 审批日志 | 审计系统导出 | 实时 | Art 14 |
| 例外处理记录 | Markdown 文档 | 按需 | Art 14（紧急覆盖） |
| 员工合规培训记录 | 培训平台导出 | 每人/每年 | Art 14（人员能力） |

#### 持续监控机制

```yaml
# .github/workflows/eu-ai-act-compliance.yml
name: EU AI Act Compliance Check

on:
  pull_request:
    paths:
      - '.agents/**'
      - '**/*.py'
      - '**/*.ts'
  schedule:
    - cron: '0 8 * * 1'  # 每周一执行

jobs:
  compliance-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify .agents/ integrity
        run: uv run .agents/scripts/check_rules.py

      - name: Run compliance scan
        run: inkog verify . --policy eu-ai-act --output json > compliance-report.json

      - name: Check compliance threshold
        run: |
          SCORE=$(jq '.governance_score' compliance-report.json)
          if [ "$SCORE" -lt 90 ]; then
            echo "❌ Compliance score ${SCORE} below threshold 90"
            exit 1
          fi
          echo "✅ Compliance score: ${SCORE}/100"

      - name: Archive report
        uses: actions/upload-artifact@v4
        with:
          name: eu-ai-act-compliance-report
          path: compliance-report.json
```

#### Pre-Deadline 最终签核清单（8/2 前 3 天完成）

```
□ Art 12 记录留存
  □ AI Agent 操作日志完整保留
  □ 日志可回溯到具体责任人
  □ 日志保留期 ≥ 法规要求

□ Art 14 人类监督
  □ 高风险操作清单已定义
  □ 每项高风险操作有明确审批流程
  □ 审批节点不可被 AI 绕过（硬阻断）
  □ 紧急覆盖流程已文档化

□ Art 15 鲁棒性
  □ Prompt Injection 防护已部署
  □ 输入净化在 LLM 调用前生效
  □ 速率限制已配置
  □ 降级/熔断策略已测试

□ 证据完整性
  □ 合规报告可生成（非空文件）
  □ Git 历史覆盖声明变更全过程
  □ 员工合规培训已完成并记录

□ 持续合规
  □ CI 合规门禁已上线
  □ 合规负责人已指定
  □ 季度复审日程已安排
```

**阶段四完成标准**：
- [x] 合规证据包完整（6 类证据齐全）
- [x] CI 门禁已上线，合规分数 ≥ 阈值
- [x] Pre-Deadline 签核清单全部通过
- [x] 合规负责人已指定，季度复审日程已定

---

### 9.5 当天即可启动的最小行动

如果团队今天（2026.6.21）才开始关注 EU AI Act，以下是最小可行步骤：

| 时间 | 动作 | 效果 |
|------|------|------|
| **今天下午** | 运行 `inkog verify . --policy eu-ai-act`（或手动填写 [9.1 差距分析表](#91-阶段一评估与差距分析第-1-周623--630)） | 知道自己的合规基线在哪里 |
| **明天** | 完成 AI 使用场景盘点，识别高风险操作 | 知道什么需要优先治理 |
| **本周内** | 创建 AGENTS.md，写入三条款合规声明 | 声明基础设施上线（证据链起点） |
| **下周** | 编写 constraints.toml，定义高风险操作清单 | 约束声明可审计 |
| **7/14 前** | 接入校验工具，完成首轮扫描与修复 | 声明与代码对齐 |
| **7/28 前** | 生成合规报告，CI 门禁上线 | 合规可自动化验证 |
| **8/2 前** | Pre-Deadline 签核 + 应急预案演练 | 有底气面对截止日 |

---

### 9.6 与现有 Level 体系的关系

```mermaid
flowchart TD
    subgraph "EU AI Act 合规时间线"
        P1["阶段一：评估<br/>（对应 Level 0 决策）"]
        P2["阶段二：治理声明层<br/>（对应 Level 4 核心能力）"]
        P3["阶段三：校验扫描层<br/>（Level 4 + 第三方工具）"]
        P4["阶段四：证据固化<br/>（Level 4 持续运营）"]
    end

    subgraph "路线图 Level 体系"
        L0["Level 0：AGENTS.md 基线"]
        L1["Level 1：规则体系"]
        L2["Level 2：技能标准化"]
        L3["Level 3：声明式治理"]
        L4["Level 4：多团队治理闭环"]
    end

    P1 --> L0
    P2 --> L3
    P2 --> L4
    P3 --> L4
    P4 --> L4
```

> **关键路径**：从零开始达到 EU AI Act 基本合规所需的最小 Level 组合 = **Level 0（AGENTS.md 基线）+ Level 4 的核心组件（constraints.toml + 角色定义）**。Level 1-3 的能力（路由表、技能标准化、world.toml）是锦上添花，非合规硬性要求。

---

## 十、验证体系

### 每个 Level 的验证方法

| Level | 验证方法 | 通过标准 | 指标归属 |
|-------|---------|---------|---------|
| Level 0 | 让 AI 执行一个任务（如"创建一个新组件"），检查输出是否遵循 AGENTS.md | 至少 3/5 条约定被遵守 | 声明层基线可见生效 |
| Level 1 | 让 AI 编辑不同语言的文件，观察日志中是否只加载对应规则 | Python 编辑不加载 frontend.md 的内容 | 声明层路由精度提升 |
| Level 2 | 在 AI 工具中触发技能调用，确认执行流程正确 | 技能产出符合 SKILL.md 定义 | 执行层复用能力形成 |
| Level 3 | 运行验证脚本检查 world.toml 引用的文件是否存在 | 零 broken references | 声明层资产完整性 |
| Level 4 | 检查子 AGENTS.md 的覆盖声明是否与父 AGENTS.md 一致 | 覆盖条目有明确理由且无冲突 | 治理闭环入口建立 |

### 指标口径：不要只看采用量，要看治理闭环度

基于更新后的竞品分析，本路线图的指标不再只看“有多少项目写了 AGENTS.md”，而改为同时观察 **声明层、执行层、验证层** 三类信号。

| 指标层 | 代表问题 | 典型指标 | 说明 |
|-------|---------|---------|------|
| **声明层** | 项目是否把治理规则写出来了？ | AGENTS.md 覆盖率、rules/ 覆盖率、constraints.toml 存在率 | 衡量入口渗透，不代表真实执行 |
| **执行层** | 规则是否真的进入日常协作与工具链？ | 技能调用成功率、审批接入率、审计接入率 | 衡量治理是否落到主链路 |
| **验证层** | 声明和行为是否能被自动证明一致？ | 校验脚本通过率、CI 门禁覆盖率、合规分数 | 衡量治理是否可持续自动化 |
| **闭环度** | 三层是否形成连续链路？ | 同时具备声明/执行/验证三层的项目占比 | 衡量 AgentForge 是否从文档协议成长为工程治理体系 |

### 推荐核心指标（方案 A 最小集）

| 指标 | Level 0-1 | Level 2-3 | Level 4 | 建议目标 |
|------|-----------|-----------|---------|---------|
| **声明层采用率** | AGENTS.md / rules/ 是否建立 | world.toml 是否纳管 | constraints.toml / 角色定义是否存在 | 团队目标项目 ≥ 80% |
| **执行层接入率** | — | 技能是否被重复调用 | 审计 / 审批 / 净化是否接入主链路 | 治理相关项目 ≥ 50% |
| **验证层覆盖率** | 基础手动验证 | 脚本校验 world.toml / 路由表 | CI 门禁 + 合规扫描 | 核心项目 ≥ 80% |
| **示范闭环项目数** | — | 1 个 | 2-3 个 | 形成对外标杆案例 |

### 可选自动化：规则文件健康检查

```python
# .agents/scripts/check_rules.py
"""检查 .agents/ 下规则文件的完整性和引用一致性"""

import tomllib
from pathlib import Path

agents_dir = Path(".agents")
world_toml = agents_dir / "world.toml"

def check_world_toml():
    if not world_toml.exists():
        print("⚠ world.toml 不存在，当前最大 Level < 3")
        return True

    with open(world_toml, "rb") as f:
        data = tomllib.load(f)

    all_ok = True
    for frag_name, frag in data.get("fragments", {}).items():
        for included in frag.get("includes", []):
            if not (agents_dir / included).exists():
                print(f"❌ [{frag_name}] 引用文件不存在: {included}")
                all_ok = False

    for rule in data.get("kernel", {}).get("rules", []):
        if not (agents_dir / rule).exists():
            print(f"❌ [kernel] 引用文件不存在: {rule}")
            all_ok = False

    if all_ok:
        print("✅ world.toml 所有引用完整")
    return all_ok

def check_routing_table():
    agents_md = Path("AGENTS.md")
    if not agents_md.exists():
        print("❌ AGENTS.md 不存在！最低要求 Level 0 未满足")
        return False

    content = agents_md.read_text(encoding="utf-8")
    if "Task Routing" not in content:
        print("⚠ AGENTS.md 缺少 Task Routing 表，当前最大 Level < 1")
    else:
        print("✅ Task Routing 表存在")
    return True

if __name__ == "__main__":
    ok = all([check_routing_table(), check_world_toml()])
    exit(0 if ok else 1)
```

将此脚本集成到 CI 中，每次 PR 自动检查：

```yaml
# .github/workflows/check-agents-md.yml
- name: Check .agents/ integrity
  run: uv run .agents/scripts/check_rules.py
```

---

## 十一、阶段成果速查

| 你的现状 | 推荐 Level | 第一步 | 预计投入 | 核心收益 | 优先观测指标 |
|---------|-----------|--------|---------|---------|-------------|
| 团队刚开始用 AI 工具，各自为战 | Level 0 | 下午花 15 分钟写 AGENTS.md | 1 小时 | AI 行为基线统一 | 声明层采用率 |
| 已有 AGENTS.md，但过长导致 AI 性能下降 | Level 1 | 拆出 rules/，加路由表 | 2 小时 | Token 消耗 -30% | 声明层路由精度 |
| 团队有重复的 AI 协作模式（如 PR Review） | Level 2 | 沉淀前 2 个技能 | 1 天 | 协作效率复用 | 执行层接入率 |
| 多模块/多子项目，AI 规则混乱 | Level 3 | 创建 world.toml + Fragments | 2 天 | 资产可管理可迁移 | 声明层资产完整性 |
| Monorepo + 多团队 + 合规需求 | Level 4 | 角色定义 + constraints.toml | 3 天 | 治理闭环 + EU AI Act 声明基础设施 | 验证层覆盖率 + 闭环度 |

### 阶段成果判断：从“写了文档”升级为“形成闭环”

| 阶段 | 过去常见判断 | 更新后建议判断 |
|------|-------------|---------------|
| **Level 0-1** | AGENTS.md 已写完 | 声明层已建立，且 AI 输出有可见改善 |
| **Level 2-3** | 技能或 world.toml 已存在 | 执行层开始进入主链路，资产可复用、可检查 |
| **Level 4** | constraints.toml 已提交 | 声明、执行、验证三层至少已打通两层，并开始形成闭环 |

> **合规速配**：仅需 EU AI Act 合规声明基础设施 → Level 4 足够。需要完整合规校验（代码扫描 + Art 12/14/15 自动映射） → Level 4 声明层 + Inkog 等第三方扫描器。两者互补，不可互相替代。
>
> **指标提醒**：不要只汇报“多少仓库已经有 AGENTS.md”，还要同步汇报：其中多少进入了执行层、多少已具备验证层、多少已经形成闭环。

---

## 十二、附录

### 附录 A：工具兼容性速查

| 工具 | 读取 AGENTS.md | 支持 .agents/rules/ | 支持 glob paths: | 支持 SKILL.md |
|------|---------------|-------------------|------------------|--------------|
| Cursor | ✅ 原生 | ✅ 通过 .cursor/rules | ✅ | 部分 |
| Claude Code | ✅ 原生（CLAUDE.md） | ✅ 通过 .claude/rules | ✅ | ✅ |
| OpenAI Codex | ✅ 原生 | 需路由表引用 | ❌ | ❌ |
| GitHub Copilot | ✅ 原生 | 需路由表引用 | ❌ | ❌ |
| Windsurf | ✅ 原生 | 需路由表引用 | 部分 | ❌ |
| Aider | ✅ 原生 | 需路由表引用 | ❌ | ❌ |
| Trae | ✅ 原生 | ✅ .spec/ 目录 | ✅ | ❌ |

> **降级原则**：不识别 `.agents/` 的工具仍可读取 AGENTS.md 的纯 Markdown 内容。路由表在降级后变为普通表格，不影响核心约束。

### 附录 B：从竞品分析到路线图的映射

本路线图直接响应了 [竞品分析](agentforge-competitive-analysis-2026.md) 中发现的**七个**核心结论：

| 竞品分析结论 | 本路线图对应章节 |
|-------------|----------------|
| AgentForge 的渐进式采用 Level 0-4 是核心差异化优势 | Level 0-4 分步实施（§1-5） |
| AGENTS.md 被 30+ 工具原生读取——这是零门槛的入口点 | Level 0：15 分钟上手（§1） |
| Token 消耗是运行时框架 10-35% 的负担 | Level 1：按需加载 rule（§2） |
| EU AI Act Art 12/14/15（2026.8.2 生效）→ 治理刚需 | §5 Level 4 声明层 + §8.5 合规分层说明 |
| AgentForge 与 Inkog 互补：声明层 + 校验扫描层 | §8.5 合规分层说明 + §8.6 合规负责人锚点 |
| 最大威胁不是竞品，是"不理解为什么要治理层" | 常见阻力及解法（§7） |
| 北极星指标不应只看采用量，还应看声明/执行/验证三层闭环度 | §10 验证体系 + §11 阶段成果速查 |

### 附录 C：参考项目

| 项目 | AGENTS.md 亮点 | 可学之处 |
|------|---------------|---------|
| AgentForge 自身 | Level 4 完整实现 | 三层架构、路由表、约束校验的示范 |
| OpenAI monorepo | 嵌套 AGENTS.md 模式 | 子项目独立路由 + 全局宪法 |
| BuildBetter BB-Skills | 条件加载技能 | AGENTS.md + 组合式技能包 |

---

*本路线图遵循渐进采用原则：不阻塞现有工作流，每一步都有可验证的收益。*
