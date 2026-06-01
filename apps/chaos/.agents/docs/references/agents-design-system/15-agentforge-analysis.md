# 15. AgentForge 专项分析

## 15.1 与主流工具的对比

| 工具/平台 | 项目级 AI 配置 | 与 AgentForge 的对应 |
|-----------|-------------|-------------------|
| **Cursor** | `.cursorrules`, `.cursor/rules/` | `AGENTS.md` ≈ `.cursorrules`，`.agents/rules/` ≈ `.cursor/rules/` |
| **Claude Code** | `CLAUDE.md` | `AGENTS.md` 职责类似，但多了 `.agents/` 子系统 |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `AGENTS.md` 定位类似，但更偏契约而非提示词 |
| **Windsurf** | `.windsurfrules` | 类似 Cursor 模式 |
| **AgentForge** | `AGENTS.md` + `.agents/` | **更完整的分层治理体系** |

**与主流工具的兼容性矩阵**（源自 AgentForge Spec v0.1）：

| 特性 | Codex CLI | Claude Code | Cursor | AgentForge |
|------|-----------|-------------|--------|------------|
| 读取 AGENTS.md | 是 | 忽略 | 忽略 | 是 |
| 解析上下文路由表 | 否 | 否 | 否 | 是 |
| 读取 .agents/rules/ | 否 | 否 | 否 | 是 |
| 解析 world.toml | 否 | 否 | 否 | 是 |
| 世界继承 | 否 | 否 | 否 | 是 |
| 技能 SKILL.md | 否 | 否 | 否 | 是 |

AgentForge 当前的状态，类似于早期 Kubernetes 之前的 Borg 论文阶段——**理念领先、运行时滞后、但骨架正确**。

与主流单智能体工具的深度对比：

| 维度 | Cursor / Claude Code | AgentForge |
|------|---------------------|------------|
| **规则形式** | 直接注入 system prompt | 声明式元数据，AI 需自行解读 |
| **角色扮演** | 用户通过对话指定 | 文件定义存在，但无自动触发 |
| **多智能体** | 不支持 | 元模型设计完备，但无运行时 |
| **质量门禁** | 依赖外部 CI | `scripts/` + `validation/` 自包含 |
| **技能体系** | 无原生技能市场 | `skills/` + `SKILL.md` + eval 闭环 |

AgentForge 的**真实差异化优势**在 `skills/` 和 `scripts/`（可执行、可验证），而非 `roles/` / `teams/`（声明式、无运行时）。

## 15.2 设计亮点

**1. 根契约 + 分层路由**：`AGENTS.md` 不做"大杂烩"，而是充当根契约 + 上下文路由器，这比 Cursor 的单文件 `.cursorrules` 更有扩展性——规则按需加载，不用一次性塞满上下文窗口。

**2. 人机文档物理隔离**：避免了"文档既要给人看又要给 AI 看"的两难。实际上 Cursor 最近也在推 `.cursor/rules/` 目录，方向是一致的。

**3. 协作元模型（Team/Role/Agent）**：不止定义"AI 怎么写代码"，还定义了**多智能体如何协作**。这在当前主流工具里还是空白地带——Cursor/Claude Code 主要解决"单个 AI 助手怎么干活"，AgentForge 已经在探索"多个 AI 怎么组队干活"。

**4. World 容器概念**：`world.toml` + `registry.toml` 把项目级 AI 配置提升到了**运行时容器**的层面。其 `kernel`（宇宙法则，不可覆盖）、`fragments`（领域能力，可安装/卸载）、`memory`（个体经验，不可移植）三层划分，本质上是用**声明式配置表达架构约束**，而不是靠代码审查或口头约定。

| world.toml 层级 | 软件架构对应 | 设计意图 |
|----------------|-------------|---------|
| `kernel`（不可缺的最小世界） | Core Domain | 任何子世界继承都不能破坏的根基 |
| `fragments`（可选能力组合） | Feature Modules | 可安装/卸载不影响基本运行 |
| `memory`（不可移植的个体经验） | Local State / Cache | 项目特有，不随世界迁移 |

**Kernel 准入标准**：进入内核的文件须满足三个条件——**不可或缺性**（缺少则世界不成立）、**普适性**（对所有子世界适用）、**稳定性**（不频繁变更）。Kernel 中通过 `immutable_rules` 列出的规则在任何子世界不可覆盖，Agent 检测到覆盖时须拒绝执行。

**多世界继承（Level 4 独家能力）**：Agent 从工作目录向上逐级查找 `AGENTS.md`，每遇到一个即注册为一个世界层级。子世界自动继承祖先世界规则，并可通过显式声明覆盖同名规则。覆盖粒度支持文件级（按文件名）、Section 级（`##` 标题）、路由表行级。推荐嵌套深度 ≤ 3 层。协作元模型：Team（治理边界）→ Role（职责模板）→ Agent（执行主体）。

## 15.3 与 MCP 的关系

[MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 是 Anthropic 推动的标准化协议，解决"AI 怎么调用外部工具"。

`AGENTS.md` + `.agents/` 可以看作 MCP 的**语义层补充**：
- **MCP** = 标准化接口（AI 能做什么）
- **AGENTS.md/.agents/** = 项目级契约（在这个项目里 AI 应该怎么做）

两者结合，才能形成完整的"工具能力 + 行为约束"。

## 15.4 竞品趋势与设计哲学对比

**设计哲学的根本分歧**：`.agents/` 的设计哲学是"世界容器"——承载完整的多智能体协作语义；`.claude/` 的设计哲学是"项目配置目录"——围绕单个工具的会话行为。`world.toml` 的 kernel→fragments→capabilities→memory 分层在主流工具中找不到对应物——Claude Code 的 `settings.json` 仅解决权限和 hooks，不触及"什么是世界的基本法则"这一元问题。

**AGENTS.md 路由化与社区共识对齐**：项目将 AGENTS.md 设计为路由文件而非知识堆，与 Claude Code 社区最佳实践共识一致——"CLAUDE.md should be a routing file, not a knowledge dump. Keep it under 200 lines."

**四大竞品趋势值得关注**：

1. **AGENTS.md 嵌套规模化**：OpenAI 主仓库自身有 88 个 AGENTS.md，大型 monorepo 按子项目拆分是主流方向。AgentForge 的多世界继承处理此问题，具有前瞻性。
2. **技能 frontmatter 控制与参数注入**：Claude Code 的 `.claude/skills/` 与 AgentForge 的 `.agents/skills/` 几乎同构，但 Claude Code 增加了 frontmatter 调用控制（`disable-model-invocation`、`user-invocable`）和参数注入（`$ARGUMENTS`），值得借鉴。
3. **子智能体记忆自动化**：Claude Code 为每个 subagent 自动维护 `MEMORY.md`，按 `memory: project | local | user` 分层。AgentForge 的 `docs/superpowers/memories/` 更概念化但缺少自动维护机制。
4. **约定变强制**：Claude Code 的 `settings.json` 包含 enforceable permissions（allow/deny 工具）和 hooks（编辑后自动跑 prettier），比纯 Markdown 规则更可靠。AgentForge 的 `.agents/` 目前全是指导性文档，缺少强制执行层。

## 15.5 各子系统逐项评估与评分

### rules/ — 核心高价值，但分布不均

| 文件 | 评估 | 说明 |
|------|------|------|
| `context-economy.md` | **高价值** | 直接解决上下文窗口痛点，有明确的操作指令 |
| `skills.md` | **高价值** | 有完整的验证体系支撑 |
| `python.md` | **中等价值** | 实用但可能与 pyproject.toml 中的约定重复 |
| `documentation.md` | **价值存疑/过厚** | 文档边界规则有用，但混入了过多"最佳实践说教" |
| `backend.md` / `frontend.md` | **价值低/过薄** | 几乎没有实质内容，要么充实，要么合并 |

**建议**：合并 `backend.md` + `frontend.md` 为 `engineering.md`；将 `documentation.md` 拆分为"可执行规则"和"参考指南"两层。

### workflows/ — PR Review 实用，Role Review 过度设计

| 文件 | 评估 |
|------|------|
| `pr-review.md` | **高价值** — 结构化的代码审查清单，AI 可直接按清单执行 |
| `role-review.md` | **过度设计** — 四道门禁设计精美但无运行时支撑 |

`role-review.md` 的核心问题：
- 谁来执行这四道门禁？如果是 AI，无证据表明 AI 会按此流程逐步审查；如果是人，这个流程对新增一个 1KB 角色文件来说过重。
- Handoff 协议是"纸面协议"：`prepared` → `accepted` → `rejected` 的状态流转没有工具记录。

**建议**：将四道门禁简化为两道（语义审查 + 合规审查），或明确标记为"草图状态，待多智能体运行时支持后激活"。

### skills/ — 真正产生业务价值的子系统 ★★★★★

Skills 是 `.agents/` 中的核心资产，有完整的"文档 + 脚本 + 测试 + 评估"闭环。应持续投入——这是 AgentForge 相对于 Cursor/Claude Code 的真正差异化资产。

### docs/ — 知识沉淀有值，但存在膨胀风险

`superpowers/` 下的 plans/specs/retrospectives 高价值，长期知识沉淀复用性强。`references/` 下部分文档如果很少被 AI 实际引用，可考虑精简或合并。

### scripts/ — 自动化是核心竞争力 ★★★★★

16+ 个脚本全部是可执行代码：`check_env.py`、`check_doc_links.py`、`check_docs_structure.py`、`check_markdown_quality.py`、`check_python_deprecations.py`、`check_world_hierarchy.py` 等，构成了**可自动化的质量门禁**，是 `.agents/` 中最"硬"的资产。

### roles/ — 形式化完备、运行时缺失 ★★☆☆☆

四个角色文件结构统一（Role Identity / Responsibilities / Default Bindings / Non-Goals）。但存在三个关键问题：

1. **没有运行时绑定机制** — AI 读取角色文件后，如何转化为实际行为？没有系统提示词模板，没有触发器，没有角色切换的显式指令。
2. **角色之间没有真实的协作记录** — 当前 AgentForge 的所有 AI 交互都是**单会话模式**，Handoff 只是纸面规范。
3. **四个角色的职责边界在实际中难以区分** — 当 AI 接到一个任务时，没有路由机制帮助它做角色选择。

对比 Cursor 的 `.cursor/rules/*.md`：Cursor 的规则是**prompt 注入**——文件内容直接作为上下文注入到 system prompt。而 AgentForge 的 roles/ 是**声明式元数据**——AI 读到后需要"理解"并"自行决定"如何扮演。

### teams/ — 单 Team 模式自我消解了语义价值 ★☆☆☆☆

只有一个 Team `core-governance`，导致"Cross-Team Policy"空转，"Member Roles 表格"只是 roles/ 的重复索引。

### world.toml — 设计精美但使用存疑 ★★☆☆☆

设计美学集中体现，但存在关键问题：谁解析这个文件？`immutable_rules` 如何强制执行？`fragments` 的 `optional = true/false` 对 AI 行为有何实际影响？建议增加"消费指南"章节，移除或注释当前无实际用途的装饰性元字段。

**总评分**：

| 子系统 | 当前价值 | 建议 |
|--------|---------|------|
| `rules/` | ★★★★☆ | 保持，合并过薄文件 |
| `skills/` | ★★★★★ | 核心资产，持续投入 |
| `scripts/` | ★★★★★ | 核心资产，持续投入 |
| `docs/` | ★★★★☆ | 保持，清理低引用文档 |
| `workflows/pr-review.md` | ★★★★☆ | 保持 |
| `workflows/role-review.md` | ★★☆☆☆ | 简化或标记为草图 |
| `roles/` | ★★☆☆☆ | 增加运行时绑定，否则降级 |
| `teams/` | ★☆☆☆☆ | 合并或引入第二 Team |
| `templates/` | ★★★☆☆ | 保持 |
| `world.toml` | ★★☆☆☆ | 增加消费指南，清理装饰字段 |

## 15.6 roles/ 和 teams/ 的增量价值深度分析

> **`roles/` 和 `teams/` 当前处于"形式化完备、运行时缺失"状态，增量价值尚未充分兑现。**

**要让 roles/ 产生真实增量价值，需要建立运行时绑定，有三种方案：**

| 方案 | 描述 | 投入 |
|------|------|------|
| **A：角色触发器（轻量）** | 在 `AGENTS.md` 的上下文路由表中增加角色列，并在每个角色文件中增加 `## System Prompt` 章节 | 低 |
| **B：多智能体编排（重量）** | 引入真正的多智能体运行时：主 AI 作为 orchestrator，按角色拆分 subagent，通过 handoff 协议状态交接 | 高 |
| **C：pragmatic 降级（务实）** | 将 roles/ 合并为 `docs/references/role-guidelines.md`，保留角色概念但不宣称"协作元模型"，精力集中在 skills/ 和 scripts/ | 低 |

## 15.7 简化与强化建议

**立即简化**：
- `teams/` — 合并到 `roles/` 或降级为 docs
- `workflows/role-review.md` — 从四道门禁简化为两道
- `backend.md` + `frontend.md` — 合并或充实
- `world.toml` 元字段 — 移除 `min-alpha` 等无运行时的装饰性字段

**中期强化**：建立角色到提示词的映射和多智能体编排的运行时。
