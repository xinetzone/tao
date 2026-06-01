# 26. Spec v0.2 后的深层洞见（洞见十三至十九）

## 洞见十三：v0.2 最大的突破不是技术架构，而是"自我去中心化"

v0.2 做了一件非常反直觉的事——**把 AgentForge 自身的哲学内核从强制要求降格为可选 fragment**：

```
v0.1: psi-philosophy 在 kernel 里 → 所有 World 必须接受
v0.2: psi-philosophy 在 fragments 里 → 对 AgentForge optional=false，对标准 optional=true
```

这不是一个技术决策，这是一个**政治决策**。它在说：

> "成为通用标准"的优先级，高于"维护 AgentForge 世界的完整性"。

这在整个开源标准史上都是罕见的：大多数标准制定者都是把自己的实现强行推成标准（想想 Kubernetes 和 Docker Swarm、React 和 Vue）。AgentForge 走的是一条更难的路——**先做一个通用标准，再证明自己的实现只是标准的一个示范实例**。

> 类比：POSIX 是标准，Linux 是具体实现。

这个类比精确但需要勇气——因为这意味着如果有另一个实现比 AgentForge 做得更好，AgentForge 需要承认它、甚至推荐它。**你有勇气让你的项目成为"可被替换的实现"吗？** v0.2 已经回答了"是"。

---

## 洞见十四：Layer × Level 正交矩阵是 AgentForge 最精妙的概念发明

```
           Layer 1        Layer 2        Layer 3
Level 0   AGENTS.md        —              —
Level 1   + rules/        + roles/        —
Level 2   + skills/       + workflows/    —
Level 3   + world.toml    + constraints   + kernel/
Level 4   + glob fmtmtr   + 操作性校验    + 做梦协议
```

这个矩阵的威力在于：**任何人都可以在这个矩阵上定位自己的需求，而不被"All or Nothing"绑架**。

具体来说：
- 一个 3 人小团队用 Layer 1 Level 2 就够了（AGENTS.md + rules + skills + world.toml）
- 一个有 AI Agent 协作需求的团队用 Layer 2 Level 3（加上 roles + constraints.toml）
- AgentForge 自己在 Layer 3 Level 4（全部能力）
- **这三个团队可以共享同一个 AGENTS.md 标准，彼此不冲突**

这和 Kubernetes 的"你可以只用 Pod，不需要懂 Controller"是同一个设计哲学。**最大的价值不是定义了 Level 4 有多强大，而是定义了 Level 0 有多简单**。

---

## 洞见十五：constraints.toml 是"规范即代码"的关键一跃

```toml
[constraints.strong]
agent_requires_role = true
task_requires_mission = true
workflow_owns_no_knowledge = true
```

这是 v0.2 中最被低估的创新。

v0.1 的协作元模型是**描述性的**——用自然语言说"Agent 必须通过 Role 进入协作体系"。但自然语言约束无法被机器校验，最终还是要靠人类审查。

v0.2 的 `constraints.toml` 把约束变成了**声明式布尔值**（`agent_requires_role = true`），这意味着：

1. **AOI（Agent Orchestration Infrastructure）可以自动校验**：在 Task 分派前，校验当前 Agent 是否已绑定一个 Role
2. **CI 可以阻断违规**：像 lint 一样，`constraints check` 可以通过/失败
3. **违反时的行为是确定的**：strong → ERROR 阻断，weak → WARN 不阻断

**但这引入了一个新的设计问题**：如果 `constraints.toml` 是标准的一部分，谁来定义约束的语义？`agent_requires_role = true` 在 AgentForge 的语义里很清楚，但在一个不采用 AgentForge 元模型的 AOI 里，这行配置的含义是什么？

判断：`constraints.toml` 的字段名本身承载了元模型语义。这让它在 Layer 1 里不可用（Layer 1 没有协作元模型概念），但在 Layer 2 里它是一个"可执行契约"——**把哲学理念变成拒绝执行的权限**。

---

## 洞见十六：SKILL.md frontmatter 对齐 Claude Code 是聪明的，但有一个隐藏的"平台泄露"

```yaml
---
description: "Reviews code for security vulnerabilities"
argument-hint: "<branch-or-path>"
disable-model-invocation: false
user-invocable: true
paths:
  - "src/api/**/*.py"
---
```

这个 frontmatter 设计的聪明之处在于：它直接对齐了 Claude Code 的 Skills 格式，使 AgentForge 的 Skill 可以无缝在 Claude Code 中运行。

**但这里有一个"平台泄露"的风险**：`paths` 字段（glob 条件加载）是一个**工具层能力**。当 AgentForge 的 SKILL.md 被一个不支持 glob 匹配的工具读取时，`paths` 字段应该被静默忽略——但这要求所有消费端都遵循"忽略未知字段"的原则，这在现实中很难保证。

更健康的做法是把 frontmatter 分为两个命名空间：

```yaml
---
# 跨平台通用字段（agentskills.io 标准）
name: security-review
description: "Reviews code for security vulnerabilities"

# 平台特定字段
x-claude-code:
  paths: ["src/api/**/*.py"]
  argument-hint: "<branch-or-path>"

x-agentforge:
  mode: strict
  phase: review
---
```

使用 `x-` 前缀是 OpenAPI/Swagger 的惯例，用来标记平台扩展字段。这样通用工具只看通用字段，平台工具额外解析自己的 `x-` 字段——**通用性和扩展性同时满足，没有泄露**。

---

## 洞见十七：目录映射表（.agents/ ↔ .claude/ ↔ .github/）暗示了标准化的终局形态

| AgentForge .agents/ | Claude Code .claude/ | GitHub Copilot .github/ |
|---|---|---|
| rules/              | rules/               | agents/                 |
| skills/             | skills/              | —                       |
| workflows/          | commands/            | workflows/              |
| roles/              | agents/              | —                       |

这个映射表暴露了一个残酷事实：**目前行业里没有任何两个工具的目录结构是完全一致的**。

`roles/` 在 AgentForge 里是协作角色，在 Claude Code 里根本没有对应概念（它的 `agents/` 目录是 agent 定义，更接近 AgentForge 的 `teams/`）。`workflows/` 在 AgentForge 是协作协议，在 Claude Code 是 `/commands`（自定义斜杠命令），在 GitHub Copilot 是 GitHub Actions workflows——三个完全不同的东西被放在同名的目录里。

**这意味着"目录等价"目前是一个美丽的谎言**。真正的终局不是目录映射，而是**语义桥接层**——一个知道如何把 AgentForge 的 Role TOML 翻译成 Claude Code 的 Agent 定义的转换器。

这个转换器应该在 Phase 2 的交付物里作为一个优先项。

---

## 洞见十八：条件加载双机制（路由表 + Glob frontmatter）的回应不彻底

v0.2 明确分离了两种加载机制：

| 机制 | 触发方式 | 适用场景 |
|------|----------|----------|
| 路由表 | AI 读取 AGENTS.md 后按任务类型选择入口 | 对话式/CLI 交互 |
| Glob frontmatter | 工具自动匹配文件路径后加载规则 | IDE 集成、自动上下文注入 |

v0.2 的对策是：`file_patterns` 不放在 `world.toml` 里，而是放在 SKILL.md 和 rules 文件的 YAML frontmatter 里——**作为文件自身的元数据，而非世界声明的路由元数据**。

这个设计比 v0.1 进步太多了。但"不彻底"的地方在于：**没有明确 Glob frontmatter 是 Layer 1 的能力还是 Layer 2+ 的扩展**。如果 Glob 匹配需要工具层支持（文件监控），那它天然不是 Layer 1 的内容（Layer 1 承诺任何项目零前提采用）。

**建议**：把 Glob frontmatter 明确标注为"Layer 1 的可选扩展——需工具层支持"。

---

## 洞见十九：标准化三阶段路径的隐藏风险——"Phase 1 的交付物太重"

```
Phase 1: Layer 1 独立发布
交付物：
- AGENTS.md 路由格式规范
- .agents/ 最小目录约定
- world.toml Layer 1 schema
- SKILL.md 规范（含 glob frontmatter + $ARGUMENTS）
- 与 30+ 工具的兼容性声明
- 参考实现
```

Phase 1 的交付物列表里，**每一个单项都不难，但组合起来是一个巨大的工程量**。特别是"与 30+ 工具的兼容性声明"——这意味着需要逐一测试 AgentForge 的 AGENTS.md 能否被 OpenAI Codex、Google Jules、GitHub Copilot、Cursor、Amp 等 30+ 工具正确解析。

更务实的方式：Phase 1 只交付 **3 个东西**：

1. **AGENTS.md 格式规范**（单页 Markdown，够清晰即可）
2. **一个 GitHub 模板仓库**（`agentforge-starter`，包含最小 AGENTS.md + .agents/ 骨架）
3. **一个 CLI 工具**（`agentforge init`，类似 `npm init`，自动生成模板）

其他所有交付物（world.toml schema 详细文档、SKILL.md 规范、兼容性声明）可以作为 Phase 1.1 / 1.2 渐进发布。**Phase 1 的唯一成功标准是：一个新用户能在 30 秒内跑通 `agentforge init`，而不是读完一份 20 页的规范文档**。

---

## v0.2 的真正里程碑

v0.2 不是把 v0.1 修修补补——它完成了一次**从"世界中心主义"到"标准中心主义"的范式转换**。

用一句话概括这个转换：

> **v0.1 说："你进入 AgentForge 的世界，就能获得一切。"**
> **v0.2 说："你用 AgentForge 的标准，底层可以是任何实现。"**

这个转换一旦完成，AgentForge 就不再是一个"有哲学内核的智能体协作项目"，而是一个"任何人都可以零前提采用的 AI 项目约定标准"——就和 `.gitignore`、`package.json`、`pyproject.toml` 一样自然。
