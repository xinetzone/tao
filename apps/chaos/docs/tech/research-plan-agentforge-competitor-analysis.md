# 示例研究计划：AI Agent 框架竞品分析

> **用途**：演示如何使用 `research-methodology-template.md` 生成实际研究计划。  
> **研究目标**：对 AgentForge 及其主要竞品（LangChain、CrewAI、AutoGen、Dify）进行系统化评估，识别差异化定位和优化方向。  
> **预计周期**：3 天（数据采集 0.5 天 + 洞察分析 0.5 天 + 框架构建 1 天 + 优化评估 1 天）

---

## 第一阶段：数据采集

### 目标
从各竞品的官网、文档、GitHub 仓库提取结构化事实数据。

### 采集对象

| 竞品 | 数据源 | 抓取方式 |
|------|--------|----------|
| LangChain | `langchain.com` + GitHub | SPA → agent-browser |
| CrewAI | `crewai.com` + GitHub | SPA → agent-browser |
| AutoGen | `microsoft.github.io/autogen` + GitHub | 静态 → defuddle |
| Dify | `dify.ai` + GitHub | SPA → agent-browser |
| AgentForge | 自身仓库 `apps/chaos/` + Spec | 本地文件 → 直接读取 |

### 采集维度

- [x] 核心定位（官网一句话描述）
- [x] 技术栈（语言、依赖、部署方式）
- [x] API 设计（Agent 定义方式、工具挂载、Memory 机制）
- [x] 多智能体协作模型（是否有原生支持，通信协议）
- [x] 生态与社区（GitHub Stars、插件/工具数量、文档完整度）
- [x] 定价模型（开源/商业/混合）

### 步骤清单

- [ ] agent-browser 并发抓取 LangChain / CrewAI / Dify 官网
- [ ] 静态抓取 AutoGen 文档站
- [ ] 本地读取 AgentForge 的 Spec v0.2 和 AGENTS.md
- [ ] 各竞品 GitHub API 拉取 Stars / Issues / 最近 commit 活跃度
- [ ] 数据完整性校验：每个竞品 ≥ 6 个维度全覆盖
- [ ] 全页截图 × 4 竞品官网

### 产出物

| 文件 | 格式 | 用途 |
|------|------|------|
| `agentforge-frameworks-structured.json` | JSON | 5 竞品 × 6 维度结构化数据 |
| `agentforge-frameworks-raw/` | 纯文本 | 各官网 innerText 原始备份 |
| `agentforge-frameworks-screenshots/` | 截图 | 各竞品首页 + 定价页 |

---

## 第二阶段：洞察分析

### 目标
从横向对比中提炼 ≥ 5 条有证据链的洞察。

### 核心研究问题

1. AgentForge 的「AGENTS.md 开放标准 + world.toml 声明式清单」在竞品中是否有等价物？
2. 竞品的多智能体协作方案与 AgentForge 的 Team/Role/Agent 元模型有何异同？
3. 各竞品的「零依赖 → 渐进扩展」路径设计如何？
4. AgentForge 的 memory / skills / rules 三层是否构成差异化？
5. 生态门槛：各竞品的首次可运行时间（Time-to-First-Agent）对比？

### 预期洞察方向（假设）

| # | 假设 | 证据来源 |
|---|------|----------|
| 1 | AgentForge 的零依赖 AGENTS.md 是唯一跨 30+ IDE 的方案 | 官网兼容性声明 + IDE 厂商支持列表 |
| 2 | 竞品多在 Agent 运行时层面竞争，缺少声明式治理层 | 各框架文档中 Team/Role 概念的搜索 |
| 3 | Dify 在低代码可视化上领先，但 Agent 协作能力弱 | Dify 文档 + 社区反馈 |
| 4 | CrewAI 的角色定义与 AgentForge Role 相似但缺少约束校验层 | CrewAI 文档 vs AgentForge constraints.toml |
| 5 | AgentForge 的生态冷启动挑战最大 | GitHub Stars / 社区活跃度横向对比 |

### 步骤清单

- [ ] 按维度横向并排整理 5 竞品数据
- [ ] 每条洞察遵循「证据链 + 推论」结构
- [ ] 关键数字提取表（Stars / API 数量 / 文档页数 / 集成 IDE 数）
- [ ] 生成 10 章报告
- [ ] 可视化：竞品定位二维图 + AgentForge 差异化雷达图

### 产出物

| 文件 | 内容 |
|------|------|
| `agentforge-competitor-insight-report.md` | 10 章标准洞察报告 |

---

## 第三阶段：框架构建与验证

### 目标
构建「AI Agent 框架评估清单」，后续任何新竞品可直接套用评分。

### 框架设计

**五维评估框架**（权重按 AgentForge 战略重点分配）：

| 维度 | 权重 | 说明 |
|------|------|------|
| 零依赖与渐进扩展 | 30% | AGENTS.md 兼容性 → .agents/ → world.toml 的路径独特性 |
| 多智能体治理 | 25% | Team/Role/Agent 元模型 vs 竞品的协作方案 |
| 生态与社区 | 20% | Stars / 插件 / IDE 合作 / 文档完整度 |
| 开发体验 | 15% | Time-to-First-Agent / API 简洁度 / 调试工具 |
| 企业就绪度 | 10% | 部署方案 / 安全模型 / 审计能力 |

### 检查点（每维 5 个）

以「零依赖与渐进扩展」维度为例：

| ID | 检查点 | 评分标准 |
|----|--------|----------|
| ZD-01 | 单一 AGENTS.md 即可工作 | 5=支持 30+ IDE / 3=支持 5+ IDE / 1=仅自有工具 |
| ZD-02 | 声明式项目清单 | 5=TOML 标准 / 3=自定义格式 / 1=无 |
| ZD-03 | 规则条件加载 | 5=glob paths: 支持 / 3=全量加载 / 1=无规则系统 |
| ZD-04 | 技能跨平台导出 | 5=SKILL.md 兼容 agentskills.io / 3=自有格式 / 1=无 |
| ZD-05 | 渐进复杂度 | 5=三级清晰 / 3=两级 / 1=全有或全无 |

### 步骤清单

- [x] 确定 5 个维度 + 权重（总和 = 1.0）
- [ ] 每维度定义 5 个检查点，配 4 级预期值（参照上表 ZD-01~05）
- [ ] 竞品分析模板填入 AgentForge 作为示例
- [ ] 边界值测试：全 1 分 / 全 3 分 / 全 5 分
- [ ] AgentForge 自身模拟评分 → 识别最低分维度

### 产出物

| 文件 | 格式 | 用途 |
|------|------|------|
| `agentforge-framework-evaluation-checklist.json` | JSON | 结构化检查清单 |

---

## 第四阶段：优化与机会评估

### 目标
基于自身评分短板，输出 AgentForge 改进方向和差异化机会。

### 优化方案示例

```
## 方案：降低 Time-to-First-Agent 至 60 秒内

### 现状问题
- 检查点 DX-01（首次可运行时间）：估计得分 2/5
- 当前：用户需理解 world.toml + AGENTS.md + .agents/ 结构才能跑通
- 竞品 CrewAI：`pip install crewai && crewai create` → 30 秒可运行

### 优化方案
- 提供 `agentforge init --quick` 一键脚手架
- 内置 3 个 starter templates（hello-agent / research-agent / multi-agent）
- AGENTS.md 顶部增加 30 秒快速开始区块

### 预算影响
| 项目 | 当前 | 优化后 | 变化 |
|------|------|--------|------|
| 开发投入 | 0 人日 | 5 人日 | +5 人日 |
| 维护成本 | 0 | 3 个模板持续更新 | 低 |

### 预期收益
| 指标 | 当前（估） | 优化后（估） | 变化 |
|------|-----------|-------------|------|
| DX-01 评分 | 2/5 | 4/5 | +2 |
| 首次可运行时间 | ~10min | ~60s | -90% |
```

### 差异化机会矩阵

```
              高零依赖/渐进扩展优势
                     │
         强化治理    │    全面领先
       （Team/Role）  │   （目标状态）
  ───────────────────┼──────────────────── 高企业就绪度
         补生态短板  │    补开发体验
       （GitHub/社区）│   （脚手架/调试）
                     │
              低零依赖/渐进扩展优势
```

### 步骤清单

- [ ] 对评分最低的维度（预估为 DX 开发体验）做根因分析
- [ ] 每个优化方案填写四段式汇报模板
- [ ] 机会评估：P0 = Time-to-First-Agent 优化 / P1 = 社区生态建设 / P2 = 企业部署方案
- [ ] 标注回避方向：不与 Dify 在低代码可视化上正面竞争

---

## 收尾：萃取与归档

### 归档清单

| 阶段 | 动作 | 目标位置 |
|------|------|----------|
| 完整留档 | 复制全部有效产物 | `.archive/agentforge-competitor-analysis-{date}/` |
| 可复用萃取 | 提炼「AI Agent 框架评估清单」 | `docs/tech/` |
| 可复用萃取 | 提炼研究方法论（如本模板自身） | `docs/tech/research-methodology-template.md` |
| 清理 | 删除 `.temp/` 中已归档文件 | — |

### 归档自检

- [ ] `.temp/` 留存文件 ≤ 原始数量的 30%
- [ ] 「AI Agent 框架评估清单」可独立用于评估任何新 Agent 框架
- [ ] 萃取文档中无 AgentForge 特有表述，已替换为通用概念
- [ ] 归档目录文件清单已记录

---

## 附录：工具链速查

| 场景 | 推荐工具 | 理由 |
|------|----------|------|
| 竞品官网抓取 | agent-browser | LangChain/CrewAI/Dify 均为 SPA |
| AutoGen 文档 | defuddle | 微软文档站为静态生成 |
| GitHub 数据 | `gh api` CLI | Stars/Issues/Commit 批量拉取 |
| 自身仓库分析 | 本地文件读取 | `apps/chaos/` 源码 + Spec |
| 评分逻辑验证 | Python 脚本 | 边界值测试 + 权重校验 |
| 任务管理 | TodoWrite | 4 阶段 × 多步骤 |

---

*示例研究计划 | 基于 research-methodology-template.md v1.0 生成 | 2026-06-21*
