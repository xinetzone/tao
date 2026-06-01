# 25. 深层洞见续编（洞见七至十二）

## 洞见七：渐进式复杂度模型（Level 0-4）是对"传播难题"的正确破局

`.agents/` 的复杂性是传播的最大阻力。Spec v0.1 草案里的 **Level 0-4 渐进式采纳模型**，恰好是对这个问题的精确回答：

```
Level 0: 仅 AGENTS.md（自由文本契约）
Level 1: AGENTS.md + .agents/rules/（拆分规则）
Level 2: AGENTS.md + world.toml + .agents/（声明式 World）
Level 3: fragments + registry（可组合能力单元）
Level 4: 多 World 继承、分裂与融合
```

**这个分层模型的精妙之处在于**：它把"认知门槛"转化为了"增长路径"。用户不需要一次理解所有概念——Level 0 的用户体验等价于写一个 CLAUDE.md，但架构上为后续升级留好了入口。

但这里有一个隐藏的张力：**AGENTS.md 的格式在 Level 0 和 Level 2+ 之间应该是一样的吗？**

Spec 草案提到了 **AGENTS.md 双分区设计**（推测是 human-readable section + machine-parseable section），这个设计如果落地会非常有价值——它允许同一个 AGENTS.md 文件在不同 Level 下承载不同的信息密度，而不需要改格式。

---

## 洞见八：路由三维触发模型是行业最优解——但 `file_patterns` 暴露了一个架构裂痕

Spec 的 `[routing]` 设计采用了**三维触发模型**：

```toml
[routing]
intents = ["python", "依赖管理"]            # 任务意图关键词
file_patterns = ["*.py", "pyproject.toml"]  # Glob 路径匹配
phases = ["execution", "review"]            # World Session 阶段
```

AgentForge 走的是**声明式路由元数据 + 运行时匹配**的路线。这在概念上是对的。

**但 `file_patterns` 的存在暴露了一个问题**：它把 Cursor 的 Glob 匹配模式直接引入了 world.toml 的规范层。

Cursor 做 Glob 匹配是因为它是工具，可以监控文件系统事件。但 AgentForge 的 Agent 面对的不是文件系统变化，而是任务上下文。**`file_patterns` 在当前 Agent 的工作方式下很难实际生效**——Agent 在接到任务时已经知道自己要做什么，不需要通过当前打开的文件来反推应该加载什么规则。

**判断**：`file_patterns` 更适合作为 **CLI 工具层** 的触发机制（比如 `world session --watch`），而不应该进入 `world.toml` 的规范 Schema。规范层应该保留 `intents` + `phases` 两个维度，`file_patterns` 降级为可选的工具层扩展。

---

## 洞见九：Skills 跨平台对齐（agentskills.io）是"成为标准"的最快路径

> 项目 `.agents/skills/` 目录下的技能格式设计目标是与 `agentskills.io` 的 `SKILL.md` 开放标准对齐

这是一个极具战略眼光的决策。agentskills.io 正在成为 Agent Skills 的"开放目录"，类似于 npm 之于 JavaScript。AgentForge 选择与它对标而不是自创格式，意味着：

1. **技能可跨平台复用**：AgentForge 的 SKILL.md 可以在其他 Agent 平台上跑，其他平台的技能也能在 AgentForge 的 World 中使用
2. **降低创作者成本**：技能开发者只需维护一份 SKILL.md，覆盖多个平台
3. **网络效应**：如果 agentskills.io 成功了，AgentForge 作为最早的对齐者，自然受益

**但需要警惕一个风险**：当前 AgentForge 的 SKILL.md 有"扩展字段（`version`、`metadata.openclaw`）和强制章节等超集设计"。这意味着 AgentForge 对标准做了**超集扩展**。

这在生态早期是合理的（标准不够用），但需要建立一条清晰的**降级路径**：当 AgentForge SKILL.md 在不支持扩展字段的平台上运行时，超集字段必须能安全忽略，核心功能不能断裂。

---

## 洞见十：Skills 校验双模式（strict/relaxed）是一套隐式的"技能成熟度模型"

```
strict 模式：7 个章节（2 必填 + 5 推荐）全部存在
relaxed 模式：仅强制 2 个最小集章节（Name + Description）
```

这个设计表面上是一个校验策略，但本质上定义了一套**技能的成熟度阶梯**：

```
relaxed 通过 = 技能可用（MVP）
strict 通过   = 技能成熟（生产级）
```

这和 Level 0-4 的渐进式复杂度模型在概念上同构——**都在用"可选的严格性"引导用户从"能用"走向"规范"**。

这个模式可以推广到更多层面：

| 层面 | MVP（relaxed） | 生产级（strict） |
|------|---------------|-----------------|
| Skills | Name + Description | 7 章节完整 |
| World | AGENTS.md 自由文本 | world.toml + fragments |
| Rules | 自由文本 Markdown | 带 intent/file_patterns 路由元数据 |
| Workflows | 自然语言描述 | 结构化步骤 + Handoff 协议 |

如果 AgentForge 能把这种"校验即成长路径"的模式系统化到整个规范体系，会成为它的又一差异化优势。

---

## 洞见十一：`tests/` 与 `evals/` 目录等价——一个被低估的设计信号

> 项目中 `tests/` 与 `evals/` 目录视为等价

这个看似微小的设计决策，实际上暗示了一个**范式的转变**：

传统软件工程中，`tests/` 验证"代码是否正确"，`evals/`（evaluations）验证"AI 输出是否令人满意"。两者是不同层级的质量保障——tests 是二元的（pass/fail），evals 是连续的（score/ranking）。

AgentForge 将两者等价处理，意味着它把 **Agent 行为的可验证性** 提升到了与传统代码测试同等的地位。这不是一个技术决策，是一个**架构哲学声明**：AI 智能体的行为应该像代码一样可测试。

但当前这个"等价"还只是命名层面的——实际落地需要更多基础设施：

- 如果 Skill 的输出是一个 PDF 转换结果，如何写"单元测试"来验证它？
- 如果 Workflow 的验证标准是"人类审查后觉得 OK"，这在 CI 里如何自动化？
- strict/relaxed 双模式校验是否也应该应用于 evals？

**`tests/` 与 `evals/` 等价是一个正确的方向，但它目前更像一个占位符，需要一个完整的 evals 框架来填实**。

---

## 洞见十二：AgentForge 的真正机会——成为"AI 原生的 package.json"

回到核心命题。当前行业里：

- **npm/package.json** 定义了 JavaScript 项目的标准
- **Cargo.toml** 定义了 Rust 项目的标准
- **pyproject.toml** 定义了 Python 项目的标准

这些都是**代码项目**的标准。但对于 **AI Agent 项目**，还没有一个被广泛接受的标准文件。

AgentForge 的 `AGENTS.md` + `world.toml` + `.agents/` 正在定义的就是这个东西。

**AgentForge 不需要赢在哲学深度，也不需要赢在元模型完整度——它需要赢在"成为 AI 原生项目的 package.json"**。

具体来说：
- `AGENTS.md` = AI 项目的 README（人类可读的入口）
- `world.toml` = AI 项目的 package.json（声明式依赖、路由、配置）
- `.agents/` = AI 项目的 node_modules/（实际资产落点）
- Registry = AI 项目的 npm registry（分发网络）

这个定位一旦清晰，所有其他设计讨论都可以收敛到一个问题：**"这个设计是否能降低 AI 项目的入门成本、提高跨项目复用率？"**

如果不能，再精妙也应该砍掉。
