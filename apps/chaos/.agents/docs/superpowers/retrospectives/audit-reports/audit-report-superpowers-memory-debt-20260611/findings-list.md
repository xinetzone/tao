# 第二章：记忆债务发现清单

## 2.1 结构债务（8 项）

#### S1-1：retrospectives/ 无前缀格式（✅ 已解决）

**现象**：14 个文件使用 `YYYY-MM-DD-<topic>.md` 格式，不包含 `task-summary-` 或 `retrospective-` 前缀。

**处置**：已逐文件判断类型并重命名——13 个为 `task-summary-`（任务执行总结），1 个为无前缀审计报告（`mise-knowledge-base-quality-audit`）。全部内部路径自引用已同步更新。

**自动化检测**：✅ 完全可行。用正则匹配 `^\d{4}-\d{2}-\d{2}-` 开头但无 `task-summary-`/`retrospective-`/`insights-` 前缀的文件。

**解决日期**：2026-06-11

#### S1-2：taolib-project-review 使用月级日期（✅ 已解决）

**现象**：`taolib-project-review-2026-05.md` 使用 `YYYY-MM` 而非 `YYYY-MM-DD`。

**审计结论**：该文件为月度项目分析报告（架构/模块/设计模式），非单日任务复盘。文件内元数据标注日期为 2026-05-23，建议后续重命名为 `taolib-monthly-review-20260523.md` 以同时体现月度语义和创建日期。当前状态可接受。

**自动化检测**：✅ 可行。正则匹配非 `\d{8}` 的日期后缀。

**解决日期**：2026-06-11

#### S2-1：retrospectives/ 四种命名格式并存（✅ 已解决）

**原始现象**：

| 格式 | 数量 | 占比 |
|------|------|------|
| `task-summary-{topic}-YYYYMMDD.md` | 42 | 64.6% |
| `YYYY-MM-DD-{topic}.md` | 14 | 21.5% |
| `{prefix}-{topic}-YYYYMMDD.md` | 8 | 12.3% |
| `{topic}-YYYY-MM.md` | 1 | 1.5% |

**处置**：S1-1 重命名消除了 14 个日期前置文件。当前格式分布：

| 格式 | 数量 | 说明 |
|------|------|------|
| `{prefix}-{topic}-YYYYMMDD.md` | ~63 | 主导格式（含 task-summary/retrospective/insights） |
| `{topic}-YYYY-MM.md` | 1 | 月级分析（已确认可接受） |
| 无前缀审计 | 1 | 专项审查（符合规范） |

格式漂移已从 4 种缩减为 2 种可接受变体（主导 + 月级），无需进一步策略制定。

**自动化检测**：✅ 完全可行。对同层文件按命名模式聚类。

**解决日期**：2026-06-11

#### S3-1：目录密度失衡

| 子目录 | 文件数 | 最后更新 | 状态 |
|--------|--------|---------|------|
| memories/ | 7 | 06-02 | 休眠中 |
| plans/ | 17 | 05-24 | 已停滞 18 天 |
| specs/ | 14 | 05-28 | 已停滞 14 天 |
| retrospectives/ | 65 | 06-11 | 持续活跃 |

retrospectives 占比 63%，memories 仅占 6.8%。文件密度比为 65:17:14:7。

**自动化检测**：✅ 完全可行。统计各子目录文件数并计算占比。

**建议**：无需立即行动。密度比反映了项目当前处于"执行+复盘密集期"，但 memory 提取管道需要后续激活。

---

## 2.2 内容债务（8 项）

#### C1-1：python315-adaptation 同日双文件（✅ 已解决）

| 文件 | 行数 | 处置 |
|------|------|------|
| `python315-adaptation-20260521.md` | 149 | 已删除 |
| `task-summary-python315-adaptation-20260521.md` | 294 → 320 | 保留，合并了短文件 §4「关键发现」为 §3.5 |

两台文件同日创建、主题相同、仅前缀不同。经章节级对比（遵照 §2.2 文件去重规则），短文件独有 §4「关键发现」（PEP 价值评估表、标准库影响分析、CVE 清单），已合并至保留文件后删除冗余。

**自动化检测**：⚠️ 部分可行。可通过文件名相似度（编辑距离/前缀剥离后比对）检测，但最终需要人工确认内容是否确实重复。

**解决日期**：2026-06-11

#### C1-2：containerrun-refactor 同日双文件（✅ 已解决）

| 文件 | 行数 | 视角 |
|------|------|------|
| `insights-containerrun-refactor-20260610.md` | 198 | 设计反思：escape hatch 模式、耦合方向、可选字段哲学 |
| `task-summary-containerrun-refactor-20260610.md` | 546 | 执行总结：5 轮改动、关键决策、问题解决 |

**审计结论**：`insights-` 原非规范前缀，现已采纳加入 `retrospective-conventions.md` §2.2。两份文件互补——task-summary 记录执行过程，insights 提炼设计原则。insights 文件已内置对 task-summary 的 `关联复盘` 引用，无需合并。

**解决日期**：2026-06-11

#### C1-3：agentforge-project 两文件 9 天间隔（✅ 已解决）

| 文件 | 行数 | 日期 | 覆盖周期 |
|------|------|------|---------|
| `agentforge-project-retrospective-20260523.md` | 575 | 05-23 | 05-18 → 05-23（Phase 1） |
| `retrospective-agentforge-project-20260601.md` | 477 | 06-01 | 05-23 → 06-01（Phase 2） |

**审计结论**：顺序回顾，非重复。06-01 已内建对 05-23 的 `上次复盘` 引用，覆盖不同时间周期。两份互补——05-23 是基线全面回顾，06-01 是增量复盘。

**解决日期**：2026-06-11

#### C1-4：taolib 版本线三文件（✅ 已解决）

| 文件 | 行数 | 类型 |
|------|------|------|
| `taolib-project-review-2026-05.md` | 264 | 月度项目分析（架构/模块/设计模式） |
| `task-summary-taolib-v040-improvements-20260523.md` | 192 | 子任务：v0.4.0 P1-P3 改进 |
| `task-summary-taolib-v040-v060-full-sprint-20260524.md` | 334 | 全量 Sprint：v0.4.0→v0.6.0（4 个版本） |

**审计结论**：三种不同报告类型，非重复。月度分析是结构性项目审查，v040-improvements 是单版本子任务细节，full-sprint 是跨版本全量执行报告。三者角度互补。

**解决日期**：2026-06-11

#### C1-5：zhihu 主题三文件（✅ 已解决）

| 文件 | 行数 | 日期 | 范围 |
|------|------|------|------|
| `zhihu-promotion-content-20260525.md` | 197 | 05-25 | 内容创作专项复盘 |
| `task-summary-zhihu-integration-20260526.md` | 475 | 05-26 | 主会话：7 Phase 全流程（学习→内容→API→Skill→注册） |
| `task-summary-zhihu-full-session-20260526.md` | 597 | 05-26 | **延续会话**：Token验证+清理+全面复盘+P1-P3改进 |

**审计结论**：覆盖不同会话/阶段，非重复。`full-session` 是 `integration` 的**延续会话**（非子集），处理前一会话未完成的 Token 验证、临时清理和改进执行。三文件互补——内容专项 + 主会话 + 延续会话。

**解决日期**：2026-06-11

#### C1-6：memories/ 同日双 principle（✅ 已解决）

| 文件 | 行数 | 维度 |
|------|------|------|
| `2026-06-02-external-knowledge-ingestion-principle.md` | 54 | **WHAT**：产出架构（sources/references/index 三层、真实源识别、轻清洗） |
| `2026-06-02-knowledge-ingestion-task-boundary-principle.md` | 54 | **HOW**：过程边界（原子提交拆分、复盘≠记忆、lint 范围管理） |

同一日期、同一主题域、均为 principle 类型、行数完全相同。

**审计结论**：两份 memory 来自不同来源任务（Hello-Agents vs DeepAgents），覆盖维度正交——一个管产出架构，一个管过程边界。**不应合并**。已双向添加 `关联记忆` 引用，明确职责边界。

**解决日期**：2026-06-11

#### C2-1：Plans/ 中的微型文件（✅ 已解决）

| 文件 | 行数 | 中位数倍数 | 处置 |
|------|------|-----------|------|
| `2026-05-23-init-onboarding-output.md` | 22 | 0.07x | ✅ 已实施，保留存档 |
| `2026-05-24-agent-context-structure-optimization.md` | 54 | 0.18x | ✅ 已实施，保留存档 |

plans/ 中位数为 299 行。22 行文件已确认非废弃草稿——plan 规定的修改（tasks.py 新增 `_print_plan`/`_print_success_next_steps`/`_print_failure` + test_tasks.py 10 个测试）已于 2026-05-23 实施完成，对应复盘 `task-summary-init-onboarding-output-20260523.md` 可印证。54 行文件也已确认实施——plan 规定的 `context-economy.md`、`documentation.md`、`python.md` 均已创建并归档于 `.agents/rules/`，AGENTS.md 亦已精简为路由入口。

**自动化检测**：✅ 可行。统计行数列，标记 < 中位数 20% 的文件。

**解决日期**：2026-06-11（22 行文件部分）

#### C2-2：Specs/ 中的微型设计（✅ 已解决）

| 文件 | 行数 | 中位数倍数 | 处置 |
|------|------|-----------|------|
| `2026-05-20-task-execution-summary-description-compression-design.md` | 31 | 0.11x | 已实施，保留存档 |
| `2026-05-20-task-execution-summary-minimal-fix-design.md` | 37 | 0.13x | 已实施，保留存档 |

两份 spec 均已实施落地——SKILL.md 升级至 v2.2（minimal-fix）+ v2.3/v2.4（description-compression），CHANGELOG 有对应版本记录。非设计碎片，是已完成的轻量设计文档。

**解决日期**：2026-06-11

---

## 2.3 流程债务（3 项）

#### F1-1：Plan 无 Spec（6 个）（✅ 已解决）

| Plan | 证据 | 状态 |
|------|------|------|
| init-onboarding-output | 复盘 + tasks.py/test_tasks.py | ✅ 已实施 |
| agent-context-structure-optimization | context-economy.md/documentation.md/python.md 已创建 | ✅ 已实施 |
| agent-token-reduction-guide | 非标准 Plan（纯知识指南），内容已通过 context-economy.md 规则落地 | ✅ 已落地 |
| cli-status-diagnostics-exploration | `.trae/specs/` 完整工作台 + 复盘 | ✅ 闭环完整 |
| exploration-reference-integrity-check | `.trae/specs/` 完整工作台 + 复盘 | ✅ 闭环完整 |
| exploration-template-reuse-check | `.trae/specs/` 完整工作台 + 复盘 | ✅ 闭环完整 |

**审计结论**：全部 6 个 Plan 均有替代证据（复盘、实施产物或规则文件）。agent-token-reduction-guide 本质是知识指南而非可执行计划，归类到 plans/ 目录属于分类偏差。其余 5 个中 2 个直接实施 + 3 个有完整 Spec 工作台。

**解决日期**：2026-06-11

#### F1-2：Spec 无 Plan（2 个）（✅ 已解决）

| Spec | 证据 |
|------|------|
| task-execution-summary-description-compression-design | 已实施：SKILL.md v2.3/v2.4 + CHANGELOG |
| task-execution-summary-minimal-fix-design | 已实施：SKILL.md v2.2 + CHANGELOG |

**审计结论**：两个 Spec 均为轻量设计文档（31/37 行），范围明确（仅修改 description / SKILL.md 定点修正），无需独立 Plan——Spec 自身已包含足够的实施指令。

**解决日期**：2026-06-11

#### F2-1：记忆提取率严重偏低

- retrospectives 已积累 **65 份**复盘报告
- memories 仅提取了 **7 条**记忆
- 提取率 = 7 / 65 ≈ 10.8%

**自动化检测**：✅ 完全可行。计算 `len(retrospectives) / len(memories)`。

**建议**：此为结构性债务，非单次人工审计可解决。需要建立常态化的"复盘→记忆提取"工作流。建议在每次 `task-summary` 产出后自动触发一次记忆候选审查。

---

## 2.4 生命周期债务（1 项）

#### L1-1：迁移存根未清理（✅ 已解决）

**文件**：`specs/2026-05-28-agentforge-spec-v0.2-three-layer-architecture.md`（9 行，纯跳转指针）

已确认迁移目标 `specs/agentforge-spec-v0.2.md` 含完整实质内容，存根已删除。

**自动化检测**：⚠️ 部分可行。检测文件行数 < 15 的文件，但需要人工确认是否为存根而非合法短文件。

**解决日期**：2026-06-11
