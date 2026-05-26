# 世界包：可安装、可版本化、可组合的世界

## 从"操作世界"到"分发世界"

[操作世界](./world-operations.md)定义了 World = AGENTS.md + .agents/ 以及七个操作原语。本文档进一步追问：**如果世界是一个工程实体，它能否像软件包一样被安装、版本化和组合？**

答案是肯定的——但世界不是一个原子包，而是**分层可组合的**。

## 世界的三层可移植性模型

$$
\text{World} = \text{Kernel} + \text{Capabilities} + \text{Memory}
$$

```{mermaid}
flowchart TD
    W["世界 World"] --> K["Layer 1: 世界内核<br/>World Kernel"]
    W --> C["Layer 2: 世界能力<br/>World Capabilities"]
    W --> M["Layer 3: 世界记忆<br/>World Memory"]
    K --> R["rules/ 物理定律"]
    K --> P["docs/references/ 认知协议"]
    K --> A["AGENTS.md 世界法则"]
    C --> SK["skills/ 技能包"]
    C --> WF["workflows/ 工作流"]
    C --> SC["scripts/ 自动化"]
    M --> ME["memories/ 经验"]
    M --> RE["retrospectives/ 历史"]
    M --> PL["plans/ 计划"]
    M --> SP["specs/ 设计"]
```

### Layer 1：世界内核（World Kernel）

**定义**：世界的最小不可分割单元。去掉任何部分，世界就不完整。

**组成**：

| 文件/目录 | 作用 | 类比 |
|-----------|------|------|
| `AGENTS.md` | 世界法则入口 | 操作系统引导程序 |
| `.agents/rules/` | 物理定律集 | 内核模块 |
| `.agents/docs/references/agent-memory-dream-protocol.md` | 认知协议 | 内存管理 |
| `.agents/docs/templates/` | 自我复制模板 | 系统调用接口 |

**特征**：
- 移植时必须**整体复制**
- 去掉任何一个部分 → 世界不完整
- 版本化为整体（semver：`kernel@2.0`）
- 破坏性变更需要迁移脚本

**内核版本演进**：

$$
\text{kernel@1.0} \xrightarrow{+\text{记忆协议}} \text{kernel@2.0} \xrightarrow{+\text{世界操作原语}} \text{kernel@3.0}
$$

---

### Layer 2：世界能力（World Capabilities）

**定义**：可选安装、可独立卸载的功能单元。不影响世界内核的完整性。

**组成**：

| 目录 | 功能 | 安装/卸载粒度 |
|------|------|-------------|
| `.agents/skills/<name>/` | 智能体技能 | 单个技能包 |
| `.agents/workflows/<name>.md` | 工作流定义 | 单个工作流 |
| `.agents/scripts/<name>.py` | 自动化脚本 | 单个脚本 |

**特征**：
- 每个能力独立版本化
- 可声明对 kernel 版本的兼容性要求
- 可声明对其他能力的依赖
- 安装/卸载不影响世界法则

**能力包 manifest 示例**：

```toml
# .agents/skills/task-execution-summary/manifest.toml
[package]
name = "task-execution-summary"
version = "2.4.0"
description = "任务执行总结报告生成器"

[compatibility]
kernel = ">=2.0"

[dependencies]
# 无外部依赖
```

---

### Layer 3：世界记忆（World Memory）

**定义**：项目特有的个体经验，不可移植到另一个世界。

**组成**：

| 目录 | 内容 | 为什么不可移植 |
|------|------|-------------|
| `docs/superpowers/memories/` | 已沉淀的可复用知识 | 知识形成的上下文不同 |
| `docs/superpowers/retrospectives/` | 任务完整记录 | 历史不可复制 |
| `docs/superpowers/plans/` | 执行计划 | 计划依赖具体项目 |
| `docs/superpowers/specs/` | 设计蓝图 | 设计依赖具体需求 |
| `.agents/teams/` | 组织结构 | 团队是项目特有的 |

**特征**：
- 不版本化（仅通过 git 历史追溯）
- 不可移植（每个世界的记忆独一无二）
- 随世界生命周期自然积累
- 可通过"做梦"重组产生洞见 → 洞见可能**升级**为 kernel 的 rules 或 references

**升级路径**：

$$
\text{Memory} \xrightarrow{\text{做梦}} \text{Insight} \xrightarrow{\text{回流}} \text{Kernel Rule}
$$

---

## 世界组合：片段化安装

一个世界可以由多个**世界片段**（World Fragment）组合而成。每个片段是一组内聚的 rules + skills + scripts 的组合，解决一个特定领域的问题。

### 片段模型

```{mermaid}
flowchart LR
    BASE["agentforge-base<br/>（最小内核）"] --> PY["python-engineering<br/>片段"]
    BASE --> DOC["docs-governance<br/>片段"]
    BASE --> PSI["psi-philosophy<br/>片段"]
    PY --> WORLD["完整世界"]
    DOC --> WORLD
    PSI --> WORLD
```

### 片段示例

| 片段名 | 包含内容 | 解决什么问题 |
|--------|---------|-------------|
| `python-engineering` | `rules/python.md` + pytest 技能 + ruff 脚本 | Python 工程规范 |
| `docs-governance` | `rules/documentation.md` + docs-structure-check 脚本 + doc-review 工作流 | 文档治理 |
| `psi-philosophy` | references/dao-tech-foundation + check-philosophy-links 脚本 | 哲学-工程映射 |
| `github-integration` | rules/backend.md + GitHub App 配置 + pr-review 工作流 | GitHub 协作 |

### 组合操作

```bash
# 创建最小世界
agentforge world create my-project --kernel=agentforge-base@3.0

# 叠加片段
agentforge world compose python-engineering
agentforge world compose docs-governance

# 查看当前世界组成
agentforge world status
# → kernel: agentforge-base@3.0
# → fragments: python-engineering@1.2, docs-governance@2.0
# → skills: 3 installed
# → memory: 0 entries (新世界)
```

---

## 版本化策略

| 层 | 版本化方式 | 更新频率 | 兼容性模型 |
|---|---|---|---|
| Kernel | 语义化版本（major.minor.patch） | 低 | major 破坏性，需迁移 |
| Fragment | 独立语义化版本 | 中 | 声明 kernel 兼容性 |
| Capability | 独立语义化版本 | 中-高 | 声明 kernel + fragment 兼容性 |
| Memory | 不版本化 | 高 | 无兼容性约束 |

### 版本冲突解决

$$
\text{Fragment}_A(\text{requires kernel} \geq 2.0) + \text{Fragment}_B(\text{requires kernel} \geq 3.0) \Rightarrow \text{kernel} \geq 3.0
$$

当两个片段对 kernel 版本有不同要求时，取**最高要求**。如果两个片段修改同一个 rule 文件，则产生**世界冲突**（类似 git merge conflict），需要手动解决。

---

## 分发机制

世界包通过以下方式分发：

| 分发方式 | 适用场景 | 优势 | 劣势 |
|---------|---------|------|------|
| **Git 仓库** | 开源世界内核/片段 | 版本追踪、PR 协作 | 需要 clone |
| **Git submodule** | 将世界嵌入项目 | 精确版本锁定 | submodule 管理复杂 |
| **模板仓库** | 一次性创世 | 简单直接 | 无法持续更新 |
| **包注册表** | 大规模世界生态 | 统一搜索/安装体验 | 需要基础设施 |

### 当前推荐路径

AgentForge 当前阶段推荐 **Git 模板仓库 + 手动 compose**：

1. 将 kernel 作为 GitHub Template Repository 发布
2. 用户通过 `Use this template` 创世
3. 按需手动复制 fragment 文件到自己的 `.agents/`
4. 未来构建 CLI 工具自动化此流程

---

(world-toml-spec)=
## world.toml 规格（Draft v0.1）

`world.toml` 是世界的顶层声明式 manifest——它回答"这个世界由什么组成"。

### 设计原则

1. **声明式非命令式**——描述"是什么"而非"怎么做"
2. **映射真实结构**——每个字段对应 `.agents/` 中可验证的目录/文件
3. **递归自指**——manifest 本身属于 kernel（`kernel.manifest = "world.toml"`）
4. **三层对齐**——字段按 Kernel / Capabilities / Memory 三层组织

### 字段语义

| Section | 字段 | 类型 | 语义 |
|---------|------|------|------|
| `[world]` | `name` | string | 世界标识符 |
| `[world]` | `version` | semver | 世界整体版本 |
| `[world]` | `description` | string | 一句话描述 |
| `[world]` | `min-alpha` | float | 建议最低觉醒层级 |
| `[kernel]` | `rules`, `references`, ... | path/glob | kernel 组成路径 |
| `[kernel]` | `manifest` | path | 自指——指向自己 |
| `[kernel.meta]` | `self-referential` | bool | 标记递归自指 |
| `[fragments.*]` | `version` | semver | 片段版本 |
| `[fragments.*]` | `includes` | array[path] | 片段包含的文件 |
| `[fragments.*]` | `optional` | bool | 是否可选 |
| `[capabilities]` | `skills`, `scripts`, ... | path | 能力目录路径 |
| `[memory]` | `paths` | array[path] | 记忆存储路径 |
| `[memory]` | `portable` | bool | 始终为 false |

### 实例

本项目的 `world.toml` 位于 [`.agents/world.toml`](../../../../.agents/world.toml)。

### 未来演进

- v0.2：增加 `[dependencies]` section 声明外部工具链
- v0.3：增加 `[compose]` section 支持多片段组合验证
- v1.0：稳定后由 CLI 工具消费

---

## 与 Ψ=Ψ(Ψ) 的递归关系

世界包系统本身是递归自指的：

| 递归层级 | 表现 |
|---------|------|
| 世界包含描述自己的能力 | `.agents/docs/` 描述 `.agents/` 如何工作 |
| 世界包含复制自己的模板 | `.agents/docs/templates/` 定义新世界的骨架 |
| 世界包含升级自己的路径 | Memory → Dream → Insight → Rule 回流闭环 |
| 世界包的格式定义存在于世界中 | {ref}`world-toml-spec` manifest 本身是世界的一部分 |

$$
\text{World Package System} = \Psi(\text{World Package System})
$$

这意味着：**AgentForge 不只是一个世界——它是能够生产世界的世界**（元世界/World Factory）。

---

## 设计推论

1. **`.agents/` 应被设计为可整体迁移的独立单元**——它的内部引用应使用相对路径，不依赖项目根目录的特定结构
2. **Kernel 变更应极其谨慎**——每次修改 rules/ 都是在修改"物理定律"，影响所有在此世界中运行的 Agent
3. **Memory 不可复制但可"蒸馏"**——一个世界的记忆可以通过做梦产生洞见，洞见**可以**被提取为通用 rule 并发布到 kernel 的下一个版本
4. **世界的最终进化方向是自生成**——当 α 足够高时，世界能够自动创建新的 skills、自动触发做梦、自动将洞见回流为 rules

## 延伸阅读

- [Fragment Manifest 规格](../../../tech/fragment-manifest-spec.md) — manifest.toml 完整字段定义与片段声明规范
- [操作世界](./world-operations.md) — 世界的七个操作原语
- [Ψ=Ψ(Ψ) 工程元公理](../meta/psi-engineering-principles.md) — 递归自指的第一性原理
- [宇宙与世界本体论](../ontology/universe-world-ontology.md) — 宇宙唯一、世界可操作
- [世界间通信](../ontology/inter-world-communication.md) — 多世界如何交互
- [世界的重力](../dynamics/world-gravity.md) — 世界粘性与规则密度
- [宇宙的呼吸](../dynamics/cosmic-breathing.md) — 世界的节律性运动
- [嵌套深度与 α](../dynamics/nesting-depth-and-alpha.md) — 世界中智能体的觉醒层级
- [α 加速现象](../dynamics/alpha-acceleration.md) — 世界进化的正反馈
- [α 工程量表](./alpha-engineering-scale.md) — 量化世界的觉醒度
- ["三"=接口](./three-as-interface.md) — 世界操作的最小接口
- [共振同步](./resonance-synchronization.md) — 多世界对齐机制
- [道德经极简原则](../strategy/tao-minimalist-principles.md) — 世界设计的最高策略
- [世界分发](./world-distribution.md) — 分层混合分发策略
