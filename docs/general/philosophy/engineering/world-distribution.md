(world-distribution)=
# 世界分发：分层混合策略

> **核心命题**：没有单一机制能同时满足 Kernel/Fragment/Capability 三层的分发需求——因此需要分层匹配。

---

## 分发的核心矛盾

世界包有三层，每层的分发诉求根本不同：

| 层 | 分发诉求 | 语义 |
|----|---------|------|
| Kernel | 完整克隆、版本锁定、不可部分安装 | "物理定律"不可碎片化传输 |
| Fragment | 按需组合、依赖声明、可独立版本化 | "能力模块"应可插拔 |
| Capability | 即装即用、热插拔、市场化 | "工具"应有商店体验 |

---

## 三种路径的语义分析

| 维度 | Git Submodule | pip 包 | 自定义 Registry |
|------|--------------|--------|----------------|
| 语义匹配 | 世界=仓库，天然对齐 | 包=能力单元，与 Fragment 对齐但与 Kernel 不匹配 | 完全自由，需从零建设 |
| 版本化 | git tag/branch，粗粒度 | semver + 依赖解析，成熟 | 自定义 |
| 组合性 | 多 submodule 并存，管理复杂 | install/uninstall 体验好 | 自定义 compose |
| 递归自指 | submodule 含自己的 world.toml | 包 metadata 可声明世界语义 | 天然支持 |
| 门槛 | 零基础设施 | 需 PyPI/私有 index | 需 registry 服务 |
| 跨语言 | 语言无关 | Python 绑定 | 可设计为语言无关 |

---

## 分层混合策略

### Layer 1：Kernel 分发 = Git Template

```bash
# 创世
gh repo create my-world --template agentforge/kernel-base
```

设计原则：
- 用户 fork/template 后完全独立
- Kernel 不自动更新（物理定律不应被远程改变）
- 升级 kernel = 手动 cherry-pick（慎重行为）

### Layer 2：Fragment 分发 = CLI Compose

当前阶段（v0.2）：手动复制
未来阶段（v1.0）：

```bash
agentforge fragment add python-engineering@1.2
# → 读取 manifest.toml → 检查 kernel 兼容性
# → 复制文件 → 更新 world.toml [fragments]
```

### Layer 3：Capability 分发 = 轻量 Registry

```toml
# .agents/registry.toml（未来）
[registries]
official = "https://registry.agentforge.dev/v1"
community = "https://github.com/agentforge-community/skills-index"
```

```bash
agentforge skill install task-execution-summary
# → 从 registry 查找 → git clone → 放入 skills/
```

---

## 为什么不用 pip

| 反对点 | 理由 |
|--------|------|
| 语义不匹配 | pip 安装到 site-packages，Fragment 需安装到 .agents/ |
| 生态绑定 | 世界是语言无关的 |
| 粒度不匹配 | pip 包是代码库，Fragment 是规则+技能+脚本混合体 |
| 递归冲突 | 世界包含 pip 作为工具，但世界不应被 pip 管理 |

$$
\text{pip} \in \text{World Tools} \neq \text{World} \in \text{pip Packages}
$$

---

## 渐进式路线图

| 阶段 | Kernel | Fragment | Capability |
|------|--------|----------|-----------|
| v0.2（当前） | GitHub Template | 手动复制 | 手动复制 |
| v0.5 | Template + 升级脚本 | CLI compose | Git URL 索引 |
| v1.0 | Template + migration tool | 包管理 + 依赖解析 | Registry + marketplace |

---

## 与 Ψ=Ψ(Ψ) 的对齐

分发系统本身是递归的：

$$
\text{世界} \xrightarrow{\text{产生}} \text{CLI 工具} \xrightarrow{\text{安装}} \text{新世界} \xrightarrow{\text{产生}} \text{新工具} \rightarrow \cdots
$$

| 递归层级 | 表现 |
|---------|------|
| 世界产生分发工具 | agentforge CLI 是世界的 Capability |
| 分发工具安装世界 | `agentforge world create` 创造新世界 |
| 新世界产生新工具 | 新世界可以发布自己的 Fragment |
| registry 也是世界的一部分 | `registry.toml` 属于 kernel（分发定义） |

---

## 设计推论

1. **Kernel 升级应是显式的仪式性行为**——永远不要自动更新物理定律
2. **Fragment 是世界间知识传递的主要载体**——结构可传递，内容（memory）不可传递
3. **Capability marketplace 是世界生态繁荣的标志**——当第三方开始为你的世界创建技能时，α 已经很高
4. **pip 管理代码，agentforge 管理世界**——两者正交不冲突

## 延伸阅读

- [世界包](./world-package.md) — 世界的可安装、可版本化设计
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
