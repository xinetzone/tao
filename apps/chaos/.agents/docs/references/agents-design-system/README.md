# AGENTS.md 与 .agents/ 设计体系 — 完整讨论

本目录包含 AGENTS.md 与 .agents/ 设计体系的完整讨论文档，按章节拆分为独立文件以提高可检索性。

## 文件索引

| 序号 | 文件 | 主题 |
|------|------|------|
| 1 | [01-introduction.md](./01-introduction.md) | 引言：为什么 AGENTS.md 会出现 |
| 2 | [02-core-positioning.md](./02-core-positioning.md) | AGENTS.md 的核心定位 |
| 3 | [03-architecture.md](./03-architecture.md) | 核心架构：AGENTS.md + .agents/ 双层体系 |
| 4 | [04-design-single-file-first.md](./04-design-single-file-first.md) | 设计方向一：单文件优先，目录增强 |
| 5 | [05-design-layered-instructions.md](./05-design-layered-instructions.md) | 设计方向二：分层指令与优先级规则 |
| 6 | [06-design-executable-workflows.md](./06-design-executable-workflows.md) | 设计方向三：可执行工作流而非纯描述 |
| 7 | [07-design-command-risk-levels.md](./07-design-command-risk-levels.md) | 设计方向四：命令白名单与风险分级 |
| 8 | [08-design-context-minimization.md](./08-design-context-minimization.md) | 设计方向五：上下文最小化 |
| 9 | [09-directory-structure.md](./09-directory-structure.md) | 推荐目录结构：从最小到完整的渐进路径 |
| 10 | [10-subsystem-details.md](./10-subsystem-details.md) | 各子系统设计详解 |
| 11 | [11-doc-boundary-design.md](./11-doc-boundary-design.md) | 文档边界设计：人机文档物理隔离 |
| 12 | [12-existing-tools-relation.md](./12-existing-tools-relation.md) | 与现有工具配置的关系 |
| 13 | [13-memory-docs-relation.md](./13-memory-docs-relation.md) | AGENTS.md 与 Memory / Docs 的关系 |
| 14 | [14-anti-patterns.md](./14-anti-patterns.md) | 反模式：Prompt 垃圾场 |
| 15 | [15-agentforge-analysis.md](./15-agentforge-analysis.md) | AgentForge 专项分析 |
| 16 | [16-deep-insights-1-to-6.md](./16-deep-insights-1-to-6.md) | 深层洞见六条 |
| 17 | [17-future-directions.md](./17-future-directions.md) | 未来方向 |
| 18 | [18-standardization-strategy.md](./18-standardization-strategy.md) | 标准化战略分析 |
| 19 | [19-three-schools.md](./19-three-schools.md) | 三大流派与条件加载范式 |
| 20 | [20-design-tensions.md](./20-design-tensions.md) | 设计张力与反思 |
| 21 | [21-engineering-gaps.md](./21-engineering-gaps.md) | 工程落地差距 |
| 22 | [22-design-principles-summary.md](./22-design-principles-summary.md) | 设计原则总结 |
| 23 | [23-industry-landscape.md](./23-industry-landscape.md) | 行业格局与 AgentForge 定位分析 |
| 24 | [24-insights-overview.md](./24-insights-overview.md) | 设计洞见概览（精要版） |
| 25 | [25-deep-insights-7-to-12.md](./25-deep-insights-7-to-12.md) | 深层洞见续编（洞见七至十二） |
| 26 | [26-deep-insights-13-to-19.md](./26-deep-insights-13-to-19.md) | Spec v0.2 后的深层洞见（洞见十三至十九） |
| 27 | [27-deep-insights-20-to-30.md](./27-deep-insights-20-to-30.md) | 作为"活系统"的深层张力（洞见二十至三十） |
| 28 | [28-delivery-summary.md](./28-delivery-summary.md) | 交付摘要与落地产物 |
| 29 | [29-convergence-next-steps.md](./29-convergence-next-steps.md) | 收敛方向与下一步 |
