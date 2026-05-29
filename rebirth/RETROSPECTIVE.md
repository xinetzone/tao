# AgentForge → WorldSprout 全面复盘

> **复盘日期**：2026-05-28
> **复盘范围**：从 Spec v0.1 到 GitHub 组织 worldsprout 注册完成的全过程
> **参与角色**：xinetzone（核心维护者）、Qoder（AI 协作者）

---

## 1. 时间线

```
2026-05-24  Spec v0.1 Draft         — 渐进式复杂度 Level 0-4
           ├── AGENTS.md 双分区设计
           ├── world.toml 三层语义模型
           └── Level 0-4: 从 AGENTS.md only 到 kernel + immutable rules

2026-05-28  Spec v0.2 Draft         — 三层分离架构
           ├── Layer 1: Project Protocol（零前提采用）
           ├── Layer 2: Collaboration Protocol（多智能体协作）
           ├── Layer 3: World Runtime（示范实现）
           ├── Layer × Level 正交矩阵
           └── 哲学内核从 kernel 必需 → Layer 3 可选 fragment

2026-05-28  Layer 1 落地
           ├── SKILL.md YAML frontmatter (description/argument-hint/paths/...)
           ├── rules/*.md 支持 paths: glob 条件加载
           ├── AGENTS.md 桥接声明（30+ 工具兼容）
           └── 6 条规则文件的 frontmatter 更新

2026-05-28  Layer 2 落地
           ├── constraints.toml（strong/weak/parallel）
           ├── 4 个 Role 声明（TOML + Markdown 双格式）
           └── 协作元模型 15 实体保持不变

2026-05-28  30 条洞见（5 轮 × 6 条/轮）
           ├── 设计层：标准分离、Layer×Level 矩阵、spec_role、语义断层线
           ├── 工程层：world init、SKILL.md 平台泄漏、dial 加载机制
           ├── 系统层：双身份张力、治理瓶颈、Registry 冷启动、dogfooding 缺口
           └── 元层级：6 条设计元洞察（design-meta-insights.md）

2026-05-28  治理基建（洞见二十→三十落地）
           ├── GOVERNANCE.md（214 行：RFC 流程、维护者权责、Layer 归属仲裁）
           ├── specs/ 目录（从 .agents/docs/superpowers/specs/ 迁出）
           ├── world.toml 增加 spec_version + spec_role 字段
           └── AGENTS.md 路由表 + 文档边界更新

2026-05-28  工具链（洞见二十七→二十九落地）
           ├── world init（starter template + 内嵌后备模板）
           ├── world guide（项目类型检测 + Fragment 推荐）
           ├── world fragment init --from-rules（规则打包为 Fragment）
           └── world init 后自动引导

2026-05-28  CI 自证（洞见二十四落地）
           ├── .agents/scripts/check_constraints.py（169 行校验器）
           ├── .github/workflows/ci.yml 新增 constraints check step
           └── .gitcode/workflows/ci.yml 同上
           └── 本地运行：✅ 所有约束校验通过

2026-05-28  组织脱胎
           ├── 命名决策：AgentForge → worldsprout
           ├── 隐喻对齐：world = 内世界容器，sprout = 种子生长
           ├── GitHub 组织 worldsprout 注册成功
           ├── rebirth/ 目录创建（3 个文件脱胎完成）
           └── taolib → sproutlib 包名重命名决策
```

---

## 2. 产出统计

| 类别 | 数量 | 关键文件 |
|------|------|----------|
| **Spec 文档** | 1 | `specs/agentforge-spec-v0.2.md`（694 行，三层分离架构） |
| **治理文档** | 1 | `GOVERNANCE.md`（214 行，RFC 流程 + 维护者模型） |
| **约束协议** | 1 | `.agents/constraints.toml`（36 行，strong/weak/parallel） |
| **Role 声明** | 4 | collaboration-architect, execution-orchestrator, governance-auditor, organization-steward |
| **规则文件** | 7 | backend, browser-agent, citations, containerization, data-flow-ordering, frontend, python（各含 paths: frontmatter） |
| **SKILL.md 更新** | 6 | pdf-to-markdown, skill-creator, task-execution-summary, zhihu-* × 4（各增加 frontmatter） |
| **CLI 源码** | 3 | init.py (234行), guide.py (230行), fragment_init.py (246行) |
| **CI 脚本** | 1 | check_constraints.py (168行) |
| **模板** | 5 | starter/ (AGENTS.md, world.toml, rules/.gitkeep, skills/.gitkeep, docs/.gitkeep) |
| **洞察文档** | 2 | design-meta-insights.md, web-content-extraction-patterns.md |
| **脱胎文件** | 3 | rebirth/worldsprout/ (README.md, AGENTS.md, world.toml) |

**总计：45 个文件变更（已提交），2,541 行新增；4 个脱胎文件（未提交）**

---

## 3. 关键决策与拐点

### 决策一：Spec v0.2 → 三层分离
**当时情境**：v0.1 的 Level 0-4 解决了"用多少"的问题，但没解决"谁用什么"——哲学内核是 kernel 的不可分割部分，任何采用 Level 3+ 的项目必须接受道德经。

**决策**：将"垂直堆叠"改为"正交分层"。Layer 定义关注点范围，Level 定义功能深度。

**后果**：
- ✅ 哲学内核降格为 Layer 3 的 psi-philosophy fragment，标准采纳者不再被迫接受世界观
- ✅ Layer 1 独立可发布，与 30+ AGENTS.md 工具生态对齐
- ⚠️ Layer × Level 正交矩阵增加了概念复杂度（虽然实际值大于代价）

### 决策二：AGENTS.md 开放标准分离声明
**当时情境**：洞见二十指出——如果 AgentForge 不声明与 AGENTS.md 标准的关系，别人会以为它是一个封闭体系。

**决策**：在 AGENTS.md 顶部、Spec §1.0、world init 模板三处同时声明"AGENTS.md 是独立社区标准，AgentForge/WorldSprout 是超集扩展"。

**后果**：
- ✅ 标准采纳者的心理门槛大幅降低——"零依赖"
- ✅ 避免了品牌混淆（AGENTS.md ≈ Markdown, WorldSprout ≈ CommonMark）

### 决策三：治理先于功能
**当时情境**：洞见三十指出——没有治理模型的标准，第一个外部贡献者问"我怎么参与？"时就会死。

**决策**：在 Spec 正式发布前，先建立 GOVERNANCE.md。

**后果**：
- ✅ RFC 流程、维护者权责、Layer 归属仲裁机制均已定义
- ⚠️ 首位核心维护者尚未任命——这是当前最大的单一风险

### 决策四：从 AgentForge 到 worldsprout
**当时情境**：AgentForge 被占用，需要新名字；同时要脱去个人身份（道德经、xinetzone、哲学驱动叙事）。

**决策**：选择 worldsprout（世界种子），隐喻对齐内世界修仙概念。

**后果**：
- ✅ "world" 保留了对 CLI（world init/guide/fragment）的完全兼容
- ✅ "sprout" 赋予了生长隐喻，与标准制定→社区共建的路线吻合
- ⚠️ taolib 包名需要改为 sproutlib（已决策，待执行）

---

## 4. 架构演进全景

```
Before (Spec v0.1):
┌─────────────────────────────────────────┐
│  Level 4: kernel + immutable rules      │
│  Level 3: world.toml + fragments        │  ← 哲学内核在此层
│  Level 2: .agents/skills/               │
│  Level 1: .agents/rules/                │
│  Level 0: AGENTS.md                     │
└─────────────────────────────────────────┘
  问题：任何 Level 3+ 项目必须接受道德经


After (Spec v0.2):
┌──────────────────────────────────────────────┐
│ Layer 1: Project Protocol                    │
│   AGENTS.md 路由 + .agents/ 最小目录         │  ← 零前提，30+ 工具兼容
│   + world.toml [world] + SKILL.md 规范       │
├──────────────────────────────────────────────┤
│ Layer 2: Collaboration Protocol              │
│   协作元模型 15 实体 + constraints.toml       │  ← 多 Agent 协作
│   + roles/teams TOML + 并行隔离              │
├──────────────────────────────────────────────┤
│ Layer 3: World Runtime                       │
│   psi-philosophy fragment (optional)          │  ← 哲学降格为可选 fragment
│   + 记忆做梦协议 + World Session              │
└──────────────────────────────────────────────┘

垂直维度：Level 0-4 渐进式复杂度（每层内部）
水平维度：Layer 1-3 关注点分离（通用→特定）


After (WorldSprout Rebirth):
┌──────────────────────────────────────────────┐
│ github.com/worldsprout/                      │
│                                              │
│   worldsprout/    spec/    registry/   privacy-spec/
│   (参考实现)      (标准)   (索引)     (隐私协议)
│                                              │
│   哲学层已完全剥离——不再需要                 │
│   道德经、Ψ=Ψ(Ψ)、马王堆帛书作为前提       │
│   "每个人都是一颗世界种子"                   │
└──────────────────────────────────────────────┘
```

---

## 5. 得失分析

### 做得好的

| 项目 | 说明 |
|------|------|
| **三层分离** | 从"垂直堆叠"到"正交分层"是一步正确的架构升级。Layer 1 让任何项目零前提入场，这是成为通用标准的必要条件。 |
| **分离声明** | AGENTS.md 标准 vs WorldSprout 扩展的类比（Markdown vs CommonMark）清晰有力，对外沟通成本极低。 |
| **约束即代码** | constraints.toml + check_constraints.py 的组合实现了洞见二十四——规范不是写在纸上的，是跑在 CI 里的。 |
| **world init 完整闭环** | 从骨架生成 → guide 推荐 → fragment 打包，30 秒内从零到第一颗种子。 |
| **治理先于发布** | 在 Spec 正式发布前建立 GOVERNANCE.md，避免了"标准有了但没人能参与"的尴尬。 |

### 需要改进的

| 项目 | 说明 |
|------|------|
| **脱胎未完成** | rebirth/ 目录只有 3 个文件（README、AGENTS.md、world.toml），GOVERNANCE.md、spec、CI 配置等尚未完成脱胎。 |
| **sproutlib 改名未执行** | taolib→sproutlib 已决策但工作量最大（32+ 文件），留给了后续 PR。 |
| **首位维护者缺失** | GOVERNANCE.md 定义了完整的治理模型，但没有实际任命任何人——这是"有宪法没总统"的状态。 |
| **隐私脱敏协议空壳** | privacy-spec/ 只存在于 README 的规划中，没有任何实际内容。 |
| **世界隐喻的边界模糊** | "世界"既是技术概念（world.toml）又是品牌隐喻（WorldSprout），两者之间的语义边界在文档中偶尔混淆。 |

---

## 6. 遗留问题（按优先级）

| P | 问题 | 状态 |
|----|------|------|
| P1 | GOVERNANCE.md 任命首位核心维护者 | 未做 |
| P1 | rebirth/ 脱胎完成（GOVERNANCE, spec, CI, .github/） | 进行中 |
| P2 | taolib → sproutlib 全项目重命名 | 已决策，待执行 |
| P2 | worldsprout 组织首个仓库推送 | 未做 |
| P3 | privacy-spec 内容起草 | 未做 |
| P3 | Registry 首个 fragment 发布 | 未做 |
| P3 | world guide 的 Fragment 推荐表充实（目前只有 python/nodejs/rust/go/web/docs/container） | 未做 |
| P4 | AgentForge 原项目（apps/chaos/）与 WorldSprout 的共存策略 | 未讨论 |

---

## 7. 下一步建议

1. **完成脱胎**：补全 rebirth/ 中 GOVERNANCE.md + Spec v1.0 + .github/ 组织配置
2. **推送首仓**：将 rebirth/worldsprout/ 作为 github.com/worldsprout/worldsprout 的第一个 commit
3. **发布 Spec v1.0**：以 WorldSprout 名义正式发布首次规范（基于 Spec v0.2 去个人化）
4. **任命维护者**：至少任命 Layer 1 的领域维护者，让标准有"可以找的人"
5. **sproutlib 改名 PR**：作为重生后的第一个 RFC 示范——展示完整的 RFC 流程

---

*复盘生成于 2026-05-28。下一个里程碑：WorldSprout Spec v1.0 正式发布。*
