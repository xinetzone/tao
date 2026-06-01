# 27. 作为"活系统"的深层张力（洞见二十至三十）

## 洞见二十：AGENTS.md 开放标准 ≠ AgentForge——但 Spec v0.2 故意模糊了这个边界

看 Spec v0.2 的兼容性声明：

```
Layer 1 与 AGENTS.md 开放标准 30+ 工具完全兼容
Layer 2 超出标准范围
Layer 3 超出标准范围
```

这里有一个微妙的语义偷换：**AGENTS.md 本身是一个独立的开放标准（由 OpenAI Codex 社区驱动），AgentForge 是它的一个"超集消费者"**。

但 Spec v0.2 把这两个东西绑定在一起叙述，给人一种"AgentForge 定义了 AGENTS.md 标准"的印象。实际上 AGENTS.md 开放标准只定义了"项目根目录放一个 AGENTS.md 文件"，没有任何目录约定、world.toml、SKILL.md 规范。

**这是一个战略性的叙事模糊**，不是事故。它让 AgentForge 在"成为标准"的路上少了一个关键步骤：说服 AGENTS.md 社区接受 AgentForge 的扩展作为标准的官方推荐实现。

**判断**：AgentForge 需要在 Phase 1 交付物里**明确一个分离声明**：

> "AGENTS.md 开放标准定义了文件存在性约定。AgentForge 定义了该文件的推荐格式和配套目录结构。两者独立，但互操作。"

不声明这个分离，一旦 AGENTS.md 社区推出自己的规范扩展，AgentForge 就会面临"标准分裂"的风险——这在开源历史上发生过无数次（Markdown → CommonMark → GFM、JSON Schema → OpenAPI）。

---

## 洞见二十一：constraints.toml 定义了"什么应该被校验"，但没有定义"谁/如何校验"

```toml
[constraints.strong]
agent_requires_role = true
task_requires_mission = true
```

Spec v0.2 提到"AOI（Agent Orchestration Infrastructure）可以自动校验合规性"。但这个 AOI **目前不存在**。

在它不存在的情况下，`constraints.toml` 的约束由谁来执行？

有三种可能的答案，每种都对应一个不同的架构路径：

| 路径 | 执行者 | 时机 | 成熟度 |
|------|--------|------|--------|
| **A. LLM 自检** | Agent 自己在每次行动前检查约束 | 推理时 | 当前可行，但不可靠 |
| **B. World CLI** | `world session` 在任务分派前校验 | 工具层 | 需要开发，中等可靠 |
| **C. AOI 中间件** | 独立的编排层拦截所有 Agent 操作 | 请求级 | 最可靠，但最远 |

当前 AgentForge 实际上走的是路径 A——靠 LLM 阅读 `constraints.toml` 后自觉遵守。这和"让律师把刑法放在桌上然后相信他不会违法"是同一个级别的可靠性。

**洞见**：Spec v0.2 把约束声明格式设计得很漂亮，但缺少一个最关键的组件——**约束执行器的参考实现**。建议：

```
Phase 2 交付物里必须加一项：
- [ ] constraints-checker：一个最小 CLI 工具，读取 constraints.toml + 当前 session 状态，输出 pass/warn/error
```

这个工具不需要完整 AOI，只需要能跑在 CI 里：`constraints-check --session .world.state/current`。**声明式约束的价值在被强制执行之前是零**。

---

## 洞见二十二：Registry 没有经济模型，而经济模型决定生态生死

AgentForge 的 Registry 系统：

```toml
[registries.local]
url = "../registry-index"

[registries.default]
url = "https://github.com/agentforge/registry-index"
```

这是一个纯技术设计——指定了从哪里获取 fragments。但它回避了一个核心问题：**谁有动力创建和维护 fragments？**

对比一下：
- npm 的经济模型：免费发布 + 企业私有 registry 付费
- Docker Hub 的经济模型：免费公开 + 私有镜像付费
- VS Code 扩展的经济模型：免费 + 微软托管成本
- pip 的经济模型：完全免费，PyPI 靠捐赠

对于 AgentForge Registry，最大的风险不是"技术上有没人用"，而是：

> 创建 fragments 的边际收益（让你的项目更规范）远低于边际成本（写 TOML、写文档、维护版本、处理冲突）。

**洞见**：AgentForge Registry 的 MVP 应该不是"能装 fragment"（这个很简单），而是**"能一键生成 fragment"**。具体来说：

```bash
# 最优体验：AgentForge 自己帮你生成 fragment
world fragment create --from-rules .agents/rules/python.md
# → 自动生成 registry-index/fragments/py/python-engineering.toml
# → 自动推断 version、includes、description
# → 提示你是否发布到远程 Registry
```

**降低创作者成本 > 降低消费者成本**。npm 成功的核心不是 `npm install` 简单（所有包管理器都一样），而是 `npm publish` 简单。

---

## 洞见二十三：.agents/ 目录结构在 v0.2 的三层映射关系存在一个"语义断层"

| 目录 | v0.1（世界完整性） | v0.2 Layer 归属 |
|------|-------------------|-----------------|
| `rules/` | kernel 不可分割 | Layer 1 最小集 |
| `skills/` | capabilities | Layer 1 最小集 |
| `docs/` | AI 知识库 | Layer 1 最小集 |
| `workflows/` | kernel | Layer 2 扩展 |
| `scripts/` | capabilities | Layer 2 扩展 |
| `templates/` | capabilities | Layer 2 扩展 |
| `roles/` | 语义目录试点 | Layer 2 扩展 |
| `teams/` | 语义目录试点 | Layer 2 扩展 |
| `kernel/` | 边界管理 | Layer 3 扩展 |

问题出在 **`workflows/` 和 `scripts/`**：

在 v0.1 里，`workflows/` 是 kernel 的一部分（`kernel.workflows = ["workflows/role-review.md"]`），意味着"缺少它世界不成立"。在 v0.2 里，它降级为 Layer 2 扩展。

但 `workflows/role-review.md` 在 AgentForge 自身世界里仍然是 kernel——它是保护角色系统边界的元机制。

**这是一个双重身份的目录**：在标准层（Layer 1/2/3 分类）里它是 Layer 2 扩展，在 AgentForge 世界（world.toml）里它是 kernel。

这意味着同样的目录在不同上下文中承载不同的"必要性权重"。目前 world.toml 没有提供一种方式来表达"这个目录在 Layer 2 定位上是扩展，但在本世界是不可或缺的"。

**洞见**：需要引入一个 `scope` 字段：

```toml
[fragments.role-governance]
version = "1.0.0"
includes = ["workflows/role-review.md"]
optional = false         # 对 AgentForge 不可选
scope = "layer2"         # 但它是 Layer 2 的内容，不是 Layer 1
```

---

## 洞见二十四：AgentForge 自身的 CI/工具链工程实践，是对其哲学主张的终极验证

回顾这个项目的工程记忆：CI 流水线系统性修复、构建系统迁移、Shell 兼容性修复、跨平台适配……每一项都是一次"反者道之动"（反馈闭环）和"弱者道之用"（柔性适配）的实战。

但有一个反讽：**AgentForge 自己并不吃自己的 dogfood**。

- AGENTS.md 定义了上下文节省规则，但 CI 修复过程中 Agent 依然需要全量加载
- constraints.toml 定义了强约束，但当前没有任何 AOI 在 AgentForge 的 CI 中执行 constraints check
- world.toml 定义了 fragments 的依赖关系，但 AgentForge 的 CI 仍然用传统的 mise/pyproject.toml 管理工具依赖

**这不是批评，而是一个机会**。AgentForge 如果能成为第一个**在自身 CI 流水线中运行 `constraints-check` 的项目**，就完成了从"规范制定者"到"规范践行者"的闭环。

具体来说，建议在 `.github/workflows/ci.yml` 中加一步：

```yaml
- name: Validate AgentForge constraints
  run: world constraints check --strict
```

如果这步失败（比如某个 Role 绑定的 rule 文件不存在），CI 就红了。**这就是"设计验证内嵌于规则本身"的终极体现**——Spec v0.2 整体架构设计里写的那个原则。

---

## 洞见二十五：标准战争的胜负不取决于规范质量，取决于"最小可感知收益"

回顾整个对话，AgentForge 已经定义了：

- 一套渐进式复杂度模型
- 一个正交三层架构
- 一个声明式世界描述语言
- 一个机器可校验的约束协议
- 一个跨工具兼容性映射表
- 一个技能分发 Registry
- 一个标准化三阶段路线图

**所有这些加起来，不如一个能让新用户在 30 秒内尖叫的体验**。

npm 的成功不是因为 `package.json` 的 Schema 设计得有多优雅，而是因为 `npm install left-pad` 太方便了。

AgentForge 需要找到自己的 "left-pad moment"——一个极其微小、但让人无法拒绝的收益瞬间。可能是：

- `agentforge init` → 自动生成一个完美的 AGENTS.md + .agents/ 骨架
- `agentforge rules add python` → 一键安装 Python 最佳实践规则
- `agentforge validate` → 一条命令校验整个项目的 Agent 规范合规性

**规范是骨架，体验是血肉。v0.2 把骨架搭得非常漂亮了。下一步，需要让它长出肉来。**

---

## 洞见二十六：AgentForge 同时是"标准制定者"和"标准消费者"——这个双重身份正在撕裂它的代码库

看一下当前仓库的实际状态：

```
world.toml          → 声明 psi-philosophy 是 optional=false 的 fragment
Spec v0.2           → 声明 psi-philosophy 是 Layer 3 可选示范
AGENTS.md           → 同时包含"通用路由表"和"本项目特有规则"
init.py             → 生成的世界模板里没有任何哲学内容
```

这四样东西说的不是同一件事。

**当 `world init` 生成一个干净的项目骨架时，它故意不包含任何哲学内容**——因为它生成的是 Layer 1 标准起点。但当你在 AgentForge 仓库里运行 `world status` 时，它展示的却是满载哲学的 Layer 3 世界。

同一个仓库，同一个 `world` 命令，在两种模式下呈现出两个不同的面孔。这不是 bug，这是**双重身份**的结构性表达。

但代码层面没有显式建模这个双重身份。`world.toml` 里没有 `mode = "standard" | "demo"` 字段。`world init` 也不知道自己是在"标准模式"下生成还是在"演示模式"下生成。

**判断**：AgentForge 需要在 `world.toml` 里增加一个顶层元字段：

```toml
[world]
name = "agentforge"
spec_version = "0.2"     # 遵循哪个版本的 Spec
spec_role = "demo"        # "standard-only" | "demo" | "consumer"
```

`spec_role = "demo"` 意味着"本世界是 Spec 的示范实现，可能包含标准范围外的内容"。`spec_role = "standard-only"` 意味着"本世界严格遵循 Spec，不含任何 Layer 3 特有内容"。`spec_role = "consumer"` 意味着"本世界只是采纳了 Spec，不参与标准化"。

**这个字段不存在，是当前代码库里最大的结构性债务**。

---

## 洞见二十七：`world init` 是 30 秒尖叫——但尖叫之后是沉默

```
$ world init --name my-project
  ✨ 项目已就绪！
    - 编辑 AGENTS.md 定制你的全局契约
    - 编辑 .agents/world.toml 声明项目元信息
    - 运行 world status 查看当前状态
```

世界生成了。然后呢？

`world init` 给你一个骨架，但**下一步没有引导**。`world status` 只会告诉你 "World: my-project (Kernel 0.1.0)"。没有 `world add python-rules`，没有 `world recommend`，没有 `world guide`。

对比一下 Cursor 的体验：安装后立即弹出 onboarding，问你要不要装推荐规则。对比一下 `npm init`：生成 `package.json` 后，你可以马上 `npm install express`。

`world init` 之后的体验是一条断头路。

**判断**：`world init` 完成后应该立即引导：

```bash
$ world init --name my-project
  ✨ 项目已就绪！

  检测到你的项目包含 Python 文件。推荐安装：
    world install python-engineering     # Python 工程规范 + 兼容性检查
    world install docs-governance         # 文档治理规则

  运行 world guide 查看完整推荐列表。
```

这不是技术问题，是体验设计问题。但**体验设计决定了标准的采纳率**——比 Schema 设计重要得多。

---

## 洞见二十八：`.agents/` 物理隔离的正确性正在被它自己的成功所挑战

Spec v0.2 坚持 `docs/`（人类）与 `.agents/`（AI）物理隔离。这个设计在哲学上无懈可击。

但看看实际发生了什么：

```
.agents/
├── docs/
│   ├── references/
│   │   ├── agent-collaboration-metamodel.md   ← AI 知识
│   │   ├── dao-tech-foundation.md             ← 哲学-工程映射
│   │   └── design-meta-insights.md            ← 设计元洞察
│   └── superpowers/
│       └── specs/
│           └── 2026-05-28-agentforge-spec-v0.2...md  ← 核心规范文档
```

现在问一个问题：**Spec v0.2 文档应该放在 `.agents/docs/` 还是 `docs/tech/`？**

它是 AI 专属的吗？不是——它同时面向人类架构师和 AI Agent。它是技术文档吗？是——它定义了文件约定和 Schema。它应该被人类开发者阅读吗？绝对是——这是项目的核心规范。

但根据隔离原则，`docs/` 放人类文档，`.agents/docs/` 放 AI 文档。那一个**同时面向两者的文档**应该放哪？

当前的选择是放在 `.agents/docs/`。但这意味着一个人类读者需要知道去 `.agents/` 里找核心规范——这恰恰是隔离原则想要避免的混乱。

**判断**：双轨分类需要一个**第三类**：`specs/`——独立于 `docs/` 和 `.agents/docs/` 的规范文档层。

```
specs/                              ← 面向任何读者的规范文档
├── agentforge-spec-v0.2.md
├── world-session-spec.md
└── routing-protocol.md

docs/                               ← 人类文档
├── tech/
└── general/

.agents/docs/                        ← AI 专属知识
├── references/
└── superpowers/
```

规范文档不属于任何一个维度——它是两个维度的公约数。把它放在任何一个维度里都会造成混淆。

---

## 洞见二十九：Registry 的"先有鸡还是先有蛋"问题——以及为什么 `world init` 是破局点

所有双边市场都面临冷启动问题：
- Registry 没有 fragments → 没人用
- 没人用 → 没人创建 fragments
- 没人创建 fragments → Registry 空的

但 AgentForge 有一个独特的破局点：**`world init` 生成的项目本身就会产生 fragment 内容**。

当一个用户运行 `world init`，然后开始写 rules——她就在**无意识地创建 fragment 内容**。她写的 `rules/python.md` 本质上就是一个 fragment。

目前的流程是断裂的：用户写了 rules，但要发布到 Registry 需要手动创建 `registry-index/fragments/` 下的 TOML 文件、填写元数据、发布。

**判断**：AgentForge 需要一个 `world fragment init` 命令：

```bash
$ world fragment init python-engineering --from-rules .agents/rules/python.md
  📦 已创建 fragment: registry-index/fragments/py/python-engineering.toml
  编辑此文件补全元数据后，运行 world publish 发布。
```

这样，**每个用 AgentForge 管理规则的项目，都天然是 Registry 的内容生产者**。冷启动问题从"怎么吸引创作者"变成"怎么让已有创作者更省力地发布"。

这恰恰是 npm 早期的成功路径——不是先有了 registry 再吸引包，而是 `npm publish` 太简单了，包自然就多了。

---

## 洞见三十：AgentForge 的真正瓶颈不是设计，不是代码，是"标准治理"

回顾整个对话——25+ 条洞见，6 条元洞察，一份 665 行的 Spec，一个 `world init` 命令。所有这些的产出者是谁？**一个人，在一个仓库里**。

这不是批评。这是事实。Linux 最初也是一个人。但 Linux 成为标准不是因为 Linus Torvalds 写了多好的代码——而是因为他建立了**内核邮件列表的治理模式**。

AgentForge 现在处于 Linus 发布 Linux 0.01 的那个时刻：东西已经能跑了，但**没有人知道怎么参与决策**。

- 如果有人想提议一个新 Layer 1 目录约定，她该怎么做？
- 如果有人觉得 `constraints.toml` 的字段名不好，RFC 流程是什么？
- 如果有人想成为 Registry 的镜像节点，审批流程是什么？
- 如果有人想 fork AgentForge 并合并回来，她该找谁？

当前的答案都是"找我"。这个答案在 v0.1 阶段没问题。但在 Spec v0.2 声称"成为通用标准"的阶段，**它是致命的**。

**判断**：Phase 1（Layer 1 独立发布）的交付物里，优先级最高的一项不应该是"与 30+ 工具的兼容性声明"，而应该是：

```
- [ ] GOVERNANCE.md — 标准治理章程
  - RFC 提交流程（模板 + 讨论期 + 决策机制）
  - 核心维护者名单与权限范围
  - Layer 归属争议的仲裁机制
  - Registry 镜像节点的准入标准
  - 版本发布周期与向后兼容承诺
```

**标准不是因为设计好而成为标准。标准是因为有人信它能活 10 年而成为标准。治理文档就是那个"10 年承诺"的具象化**。
