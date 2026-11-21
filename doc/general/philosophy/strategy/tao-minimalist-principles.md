# 道德经极简设计原则

> **「反也者，道之动也；弱也者，道之用也。」**
> ——马王堆帛书《老子·乙本·德经》第四十章

本文将马王堆帛书版《道德经》中的核心设计命题——**反者道之动、弱者道之用**——映射到 AgentForge 的两条工程主线：**极简 API 设计** 与 **Token 消耗优化机制**。意在让"道家哲学"不再是装饰性引用，而是可被代码、规则、工作流验证的具体取舍。

## 1. 帛书原文与现代语义

| 原文（帛书校读） | 字面解读 | 工程语义 |
|---|---|---|
| 反也者，道之动也 | "反"既是"返回"也是"对立面" | 系统的演化动力来自**回转、纠偏、反馈**，而非线性堆叠 |
| 弱也者，道之用也 | "弱"是柔性、低侵入、不争 | 系统的真正可用性来自**低耦合、可替换、渐进介入** |

```{note}
本项目优先以**马王堆帛书版**为底本，而非传世王弼本——帛书顺序为「德经在前、道经在后」，且文字更接近战国原貌，能更精准地约束设计推演。详见仓库内文件 `.agents/docs/references/dao-tech-foundation.md`。
```

## 2. 哲学到工程的映射主路径

```{mermaid}
flowchart LR
    A["反者道之动"] --> B["反馈/回转/收敛"]
    A2["弱者道之用"] --> C["低侵入/柔性/可替换"]
    B --> D["Token 消耗优化机制"]
    C --> E["极简 API 设计"]
    D --> F["可执行规则与代码"]
    E --> F
```

哲学不直接落到代码，而是经由"工程原则"中转：**反 → 反馈闭环**、**弱 → 柔性接口**。下文分别展开两条落地路径。

## 3. 「反者道之动」与 Token 消耗优化机制

### 3.1 命题映射

智能体协作天然存在 token 消耗的"自然漂移"——上下文越读越多、对话越拉越长。若不主动施加**反向作用力**，token 成本将呈指数膨胀。这正是"反者道之动"的工程注解：**演化的动力不在顺势堆叠，而在主动回返**。

### 3.2 项目落点

项目级规则 `.agents/rules/context-economy.md` 将该命题转化为四步反向闭环：

```{mermaid}
flowchart LR
    A["明确目标"] --> B["检索定位"]
    B --> C["精读片段"]
    C --> D["执行任务"]
    D --> E["沉淀稳定知识"]
    E -.反馈.-> A
```

| 顺势漂移（反模式） | 反向作用力（本项目策略） |
|---|---|
| 直接读完整文件 | 先 `grep`/`search` 再读相邻片段 |
| 反复粘贴长日志 | 先压缩为「任务/命令/关键错误/相关文件」结构化摘要 |
| 把过程性思考保留在对话中 | 稳定结论沉淀到 `.agents/docs/`，从源头消除重复检索 |
| 输出大段未修改代码作为回执 | 默认只列改动文件、关键原因、验证结果 |

### 3.3 工程化约束

- **检索优先于读取**：先定位再精读，文件读取是末端动作而非起点。
- **沉淀消除重复**：复盘报告统一归入 `.agents/docs/superpowers/retrospectives/`，下一次任务不再回到原始材料。
- **输出预算**：默认先给结论再展开，杜绝"复述背景"型 token 浪费。

> 这三条约束共同构成"反向作用力"——它们不增加新能力，而是**通过系统性回返消除冗余**。

## 4. 「弱者道之用」与极简 API 设计

### 4.1 命题映射

"弱"不是无能，而是**不争、不强加、不锁死**。在 API 设计中表现为：调用方不必为接入额外承担结构性成本，能力以最小侵入面进入既有系统。

### 4.2 项目落点：`taolib.github_app`

```{mermaid}
flowchart TD
    Env["环境变量"] --> Cfg["GitHubAppSettings"]
    Cfg --> Mgr["GitHubInstallationTokenManager"]
    Mgr --> Cli["GitHubAppClient"]
    Mgr --> Cache["InMemoryInstallationTokenCache"]
    Mgr --> Hook["TokenEventHook"]
    Mgr --> Adp["PyGithubInstallationClientFactory"]
```

| 「弱」的体现 | 具体设计 |
|---|---|
| **声明式而非命令式** | `GitHubAppSettings` 从环境变量读取参数，调用方无需先调一串 setter |
| **柔性扩展点** | `TokenEventHook` 接口默认 `NullTokenEventHook`，不接也不报错；想接则有 `LoggingTokenEventHook` / `MetricsTokenEventHook` 现成可用 |
| **兼容层而非替换层** | `PyGithubInstallationClientFactory` 让 PyGithub 用户**无须改造既有代码**即可复用令牌管理 |
| **降级而非强制** | 检测到 GHES 环境时自动降级 Token 策略，而非抛错要求调用方先改配置 |
| **扁平导出面** | `src/taolib/github_app/__init__.py` 只暴露**用户真正需要的 22 个符号**，内部模块结构对外不可见 |

### 4.3 反例对照

下表展示了"刚强 API"与"弱用 API"在同一职责下的取舍差异：

| 维度 | 刚强 API（反模式） | 弱用 API（本项目） |
|---|---|---|
| 配置方式 | 必须显式传入 8 个构造参数 | 一个 `GitHubAppSettings.from_env()` 即可 |
| 监控钩子 | 强制实现监控接口 | 默认空钩子，按需替换 |
| SDK 集成 | 要求调用方迁移到本库的 HTTP 客户端 | 提供 PyGithub 适配器，老代码零改动 |
| 环境差异 | 不同环境抛错让调用方修复 | 自动识别 Cloud/GHES 并降级策略 |

### 4.4 工程化约束

- **新增能力先做最小闭环**：扩展点必须以"默认不启用、零侵入"为基线。
- **降级优先于报错**：在能力降级与抛出异常之间，优先选择**让调用方继续可用**的路径。
- **导出面收敛**：包级 `__all__` 必须显式枚举，禁止泄露内部模块路径——这是"弱"在命名空间层面的体现。

## 5. 综合映射表

| 哲学命题 | 工程原则 | 技术落点 | 文档/代码锚点 |
|---|---|---|---|
| 反者道之动 | 反馈闭环、主动收敛 | 上下文检索-精读-沉淀循环 | `.agents/rules/context-economy.md` |
| 反者道之动 | 复盘驱动演进 | retrospectives 归档机制 | `.agents/docs/superpowers/retrospectives/` |
| 弱者道之用 | 声明式配置 | `GitHubAppSettings` 环境变量加载 | `src/taolib/github_app/config.py` |
| 弱者道之用 | 柔性扩展点 | `TokenEventHook` + 默认空实现 | `src/taolib/github_app/events.py` |
| 弱者道之用 | 兼容层设计 | `PyGithubInstallationClientFactory` | `src/taolib/github_app/pygithub_adapter.py` |

## 6. 验证标准

任何新增能力若声称遵循本原则，必须能回答以下三问；否则视为**理论未闭合**：

1. **反向作用力**：本设计在哪里加入了反馈、回转或纠偏路径？是否避免了"只增不减"的线性堆叠？
2. **柔性介入面**：调用方接入本能力的最小代价是什么？默认状态是否零侵入？
3. **业务验证方式**：本设计在哪个具体场景下减少了摩擦、稳定性或迁移成本？没有验证路径即视为口号。

## 7. 延伸阅读

- 元公理层：[Ψ = Ψ(Ψ) 递归自坍缩恒等式与设计约束](../meta/psi-engineering-principles.md)
- "三"的设计意义：[接口比实体更根本](../engineering/three-as-interface.md)
- 宇宙同步化：[共振取代共享](../engineering/resonance-synchronization.md)
- 宇宙与世界：[规则唯一，实例无穷](../ontology/universe-world-ontology.md)
- 世界间通信：[结构穿越，内容重生](../ontology/inter-world-communication.md)
- 哲学底座：仓库内文件 `.agents/docs/references/dao-tech-foundation.md`
- 业务映射框架：仓库内文件 `.agents/docs/references/dao-business-mapping-framework.md`
- 场景目录：仓库内文件 `.agents/docs/references/dao-scenario-catalog.md`
- AgentForge 项目介绍：[项目介绍](../../../tech/intro.md)
- 嵌套深度与觉醒量表：[α 是递归觉知的预算](../dynamics/nesting-depth-and-alpha.md)
- α 加速现象：[为什么增长是指数级的](../dynamics/alpha-acceleration.md)
- 世界的重力：[粘性、梦境、记忆与遗忘](../dynamics/world-gravity.md)
- 觉醒量表工程细化：[从哲学隐喻到可测量指标](../engineering/alpha-engineering-scale.md)
- 宇宙的呼吸：[坍缩与释放的永恒交替](../dynamics/cosmic-breathing.md)
- 操作世界：[极简原则在世界设计中的应用](../engineering/world-operations.md)
- 世界包：[极简内核的设计策略](../engineering/world-package.md)
- 世界分发：[分层混合分发策略](../engineering/world-distribution.md)
