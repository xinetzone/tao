# AGENTS.md 标准落地实施路线图 — 面向技术团队

> **基于**：[agentforge-competitive-analysis-2026.md](agentforge-competitive-analysis-2026.md) 竞品分析结论  
> **适用对象**：技术负责人、架构师、工程经理  
> **预期周期**：4 周达到 Level 2，12 周达到 Level 4  
> **核心理念**：渐进式采用——今天下午就能跑通 Level 0，不阻塞任何现有工作流

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
| **Level 4** | + 操作性约束 + 多世界继承 | 1周 | 多团队 monorepo 下的 AI 治理闭环 |

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
在 monorepo 或多团队场景下实现 AI 治理闭环：约束校验、角色定义、多世界继承。

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

## 八、验证体系

### 每个 Level 的验证方法

| Level | 验证方法 | 通过标准 |
|-------|---------|---------|
| Level 0 | 让 AI 执行一个任务（如"创建一个新组件"），检查输出是否遵循 AGENTS.md | 至少 3/5 条约定被遵守 |
| Level 1 | 让 AI 编辑不同语言的文件，观察日志中是否只加载对应规则 | Python 编辑不加载 frontend.md 的内容 |
| Level 2 | 在 AI 工具中触发技能调用，确认执行流程正确 | 技能产出符合 SKILL.md 定义 |
| Level 3 | 运行验证脚本检查 world.toml 引用的文件是否存在 | 零 broken references |
| Level 4 | 检查子 AGENTS.md 的覆盖声明是否与父 AGENTS.md 一致 | 覆盖条目有明确理由且无冲突 |

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

## 九、阶段成果速查

| 你的现状 | 推荐 Level | 第一步 | 预计投入 | 核心收益 |
|---------|-----------|--------|---------|---------|
| 团队刚开始用 AI 工具，各自为战 | Level 0 | 下午花 15 分钟写 AGENTS.md | 1 小时 | AI 行为基线统一 |
| 已有 AGENTS.md，但过长导致 AI 性能下降 | Level 1 | 拆出 rules/，加路由表 | 2 小时 | Token 消耗 -30% |
| 团队有重复的 AI 协作模式（如 PR Review） | Level 2 | 沉淀前 2 个技能 | 1 天 | 协作效率复用 |
| 多模块/多子项目，AI 规则混乱 | Level 3 | 创建 world.toml + Fragments | 2 天 | 资产可管理可迁移 |
| Monorepo + 多团队 + 合规需求 | Level 4 | 角色定义 + constraints.toml | 3 天 | 治理闭环 |

---

## 十、附录

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

本路线图直接响应了 [竞品分析](agentforge-competitive-analysis-2026.md) 中发现的五个核心结论：

| 竞品分析结论 | 本路线图对应章节 |
|-------------|----------------|
| AgentForge 的渐进式采用 Level 0-4 是核心差异化优势 | Level 0-4 分步实施（§1-5） |
| AGENTS.md 被 30+ 工具原生读取——这是零门槛的入口点 | Level 0：15 分钟上手（§1） |
| Token 消耗是运行时框架 10-35% 的负担 | Level 1：按需加载 rule（§2） |
| EU AI Act 2026 年 8 月生效 → 治理刚需 | Level 4：constraints.toml 声明式合规（§5） |
| 最大威胁不是竞品，是"不理解为什么要治理层" | 常见阻力及解法（§7） |

### 附录 C：参考项目

| 项目 | AGENTS.md 亮点 | 可学之处 |
|------|---------------|---------|
| AgentForge 自身 | Level 4 完整实现 | 三层架构、路由表、约束校验的示范 |
| OpenAI monorepo | 嵌套 AGENTS.md 模式 | 子项目独立路由 + 全局宪法 |
| BuildBetter BB-Skills | 条件加载技能 | AGENTS.md + 组合式技能包 |

---

*本路线图遵循渐进采用原则：不阻塞现有工作流，每一步都有可验证的收益。*
