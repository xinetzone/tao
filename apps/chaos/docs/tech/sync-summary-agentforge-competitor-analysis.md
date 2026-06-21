# 研究计划同步摘要：AI Agent 框架竞品分析

> 基于 [research-plan-agentforge-competitor-analysis.md](research-plan-agentforge-competitor-analysis.md) 精简 | 2026-06-21

---

## 一句话

对 LangChain / CrewAI / AutoGen / Dify 做结构化竞品分析，输出 AgentForge 差异化定位和 P0-P2 改进方向。

## 对象范围

| 对象 | 侧重点 |
|------|--------|
| LangChain | Agent 运行时 + 工具链生态 |
| CrewAI | 多智能体角色编排 |
| AutoGen（微软） | 多 Agent 对话与协作 |
| Dify | 低代码可视化 AI 应用 |

## 四阶段计划

| 阶段 | 做什么 | 产出 |
|------|--------|------|
| ① 数据采集 | 抓取 4 竞品官网 + GitHub（Stars/Issues/活跃度），6 维度 × 5 对象 | 结构化 JSON + 截图 |
| ② 洞察分析 | 横向对比，提炼 ≥ 5 条证据链式洞察 | 10 章报告 + 差异化雷达图 |
| ③ 框架构建 | 建立「AI Agent 框架评估清单」（5 维 × 25 检查点） | 评分 JSON + 竞品模板 |
| ④ 优化评估 | 基于自身评分短板出可落地方案 | 优化方案 + 机会矩阵 |

## 核心研究问题

1. AGENTS.md 零依赖方案在竞品中是否有等价物？—— 决定"零依赖"是否是真实壁垒
2. Team/Role/Agent 元模型 vs 竞品协作方案差异多大？—— 决定治理层差异化空间
3. 各竞品"零依赖→渐进扩展"路径如何设计？—— 决定 onboarding 体验对标基准
4. memory/skills/rules 三层是否构成壁垒？—— 决定长期护城河方向
5. Time-to-First-Agent 对比，差距在哪？—— 决定最紧迫的 P0 改进项

## 预期输出

- 一份可复用的「AI Agent 框架评估清单」（后续新竞品直接套用评分）
- AgentForge 差异化定位雷达图 + 机会矩阵
- ≥ 1 个 P0 改进方案（预估：Time-to-First-Agent 优化，目标 60 秒可运行）

## 需要对齐

- [ ] **竞品范围**：当前 4 个竞品是否足够？建议增加 OpenAI Agents SDK 和 Anthropic MCP 生态做对标，但会增加采集工作量约 40%。—— **A 增 / B 不增**
- [ ] **权重分配**：零依赖 30% > 治理 25% > 生态 20% > 体验 15% > 企业 10%。这个优先级是否反映当前战略重点？—— **A 认可 / B 调整**
- [ ] **数据采集分工**：agent-browser 操作谁来执行？需要 3 个 SPA 站点并发抓取。—— **提议：[人名] 负责，预计 0.5 天**

---

*1 页摘要 | 团队同步用 | 完整计划见 `docs/tech/research-plan-agentforge-competitor-analysis.md`*
