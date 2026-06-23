# 迁移日志

> **维护责任人**：Leader Agent
> **迁移日期**：2026-06-23
> **适用范围**：`plans/` 全目录
> **原始文件总数**：27 份（含 github-app 子目录的 9 个片段）

本文件记录 `plans/` 目录模块化重构的完整迁移过程，覆盖全部 27 份原始文件（18 个原始计划 + github-app 子目录的 9 个片段），含迁移去向、拆分状态与校验结果。

## 迁移总表

| # | 原始文件名 | 一级模块 | 是否拆分 | 迁移去向 | 校验状态 |
|---|-----------|---------|---------|---------|---------|
| 1 | `2026-05-22-ai-docs-navigation.md` | ai-docs | 否 | `ai-docs/2026-05-22-ai-docs-navigation.md` | ✅ 通过 |
| 2 | `2026-05-22-ai-docs-search-keywords.md` | ai-docs | 否 | `ai-docs/2026-05-22-ai-docs-search-keywords.md` | ✅ 通过 |
| 3 | `2026-05-22-ai-reference-wiki.md` | ai-docs | 是（拆分为 6 个文件） | `ai-docs/2026-05-22-ai-reference-wiki/`（含 index + 5 个任务单元） | ✅ 通过 |
| 4 | `2026-05-22-github-app-installation-token-override.md` | github-integration | 是（拆分为 10 个文件，含 9 个片段） | `github-integration/2026-05-22-github-app-installation-token-override/`（含 index + 9 个片段） | ✅ 通过 |
| 5 | `2026-05-22-pygithub-adapter.md` | github-integration | 是（拆分为 4 个文件） | `github-integration/2026-05-22-pygithub-adapter/`（含 index + 3 个任务单元） | ✅ 通过 |
| 6 | `2026-05-23-dao-business-mapping-framework.md` | docs-governance | 是（拆分为 6 个文件） | `docs-governance/2026-05-23-dao-business-mapping-framework/`（含 index + 5 个任务单元） | ✅ 通过 |
| 7 | `2026-05-23-init-onboarding-output.md` | docs-governance | 否 | `docs-governance/2026-05-23-init-onboarding-output.md` | ✅ 通过 |
| 8 | `2026-05-23-mise-single-source-foundation.md` | python-environment | 是（拆分为 7 个文件） | `python-environment/2026-05-23-mise-single-source-foundation/`（含 index + file-structure + 4 个任务单元 + plan-self-review） | ✅ 通过 |
| 9 | `2026-05-24-agent-collaboration-metamodel.md` | agent-system | 是（拆分为 5 个文件） | `agent-system/2026-05-24-agent-collaboration-metamodel/`（含 index + 4 个任务单元） | ✅ 通过 |
| 10 | `2026-05-24-agent-context-structure-optimization.md` | agent-system | 否 | `agent-system/2026-05-24-agent-context-structure-optimization.md` | ✅ 通过 |
| 11 | `2026-05-24-agent-memory-dream-protocol.md` | agent-system | 是（拆分为 8 个文件） | `agent-system/2026-05-24-agent-memory-dream-protocol/`（含 index + overview + file-structure + self-review + 4 个任务单元） | ✅ 通过 |
| 12 | `2026-05-24-agent-token-reduction-guide.md` | agent-system | 否 | `agent-system/2026-05-24-agent-token-reduction-guide.md` | ✅ 通过 |
| 13 | `2026-05-24-cli-status-diagnostics-exploration.md` | exploration | 是（拆分为 3 个文件） | `exploration/2026-05-24-cli-status-diagnostics-exploration/`（含 index + exploration-check + retrospective） | ✅ 通过 |
| 14 | `2026-05-24-exploration-reference-integrity-check.md` | exploration | 是（拆分为 3 个文件） | `exploration/2026-05-24-exploration-reference-integrity-check/`（含 index + check-record + retrospective） | ✅ 通过 |
| 15 | `2026-05-24-exploration-template-reuse-check.md` | exploration | 是（拆分为 3 个文件） | `exploration/2026-05-24-exploration-template-reuse-check/`（含 index + check-record + retrospective） | ✅ 通过 |
| 16 | `2026-05-24-knowledge-driven-exploration-foundation.md` | exploration | 是（拆分为 7 个文件） | `exploration/2026-05-24-knowledge-driven-exploration-foundation/`（含 index + 6 个任务单元） | ✅ 通过 |
| 17 | `2026-05-24-role-review-workflow.md` | agent-system | 是（拆分为 6 个文件） | `agent-system/2026-05-24-role-review-workflow/`（含 index + 5 个任务单元） | ✅ 通过 |
| 18 | `2026-06-23-memories-modular-refactor-plan.md` | docs-governance | 否 | `docs-governance/2026-06-23-memories-modular-refactor-plan.md` | ✅ 通过 |
| 19 | `github-app/file-structure.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/file-structure.md` | ✅ 通过 |
| 20 | `github-app/metrics-comparison.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/metrics-comparison.md` | ✅ 通过 |
| 21 | `github-app/plan-self-review.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/plan-self-review.md` | ✅ 通过 |
| 22 | `github-app/task-1-config-layer.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/task-1-config-layer.md` | ✅ 通过 |
| 23 | `github-app/task-2-github-client.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/task-2-github-client.md` | ✅ 通过 |
| 24 | `github-app/task-3-cache-token-manager.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/task-3-cache-token-manager.md` | ✅ 通过 |
| 25 | `github-app/task-4-single-flight-fallback.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/task-4-single-flight-fallback.md` | ✅ 通过 |
| 26 | `github-app/task-5-cli-diagnosis.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/task-5-cli-diagnosis.md` | ✅ 通过 |
| 27 | `github-app/task-6-docs-ci-report.md` | github-integration | 否（片段） | `github-integration/2026-05-22-github-app-installation-token-override/task-6-docs-ci-report.md` | ✅ 通过 |

## 迁移统计

| 维度 | 指标 | 数值 |
|------|------|------|
| 原始文件总数 | — | 27 |
| 未拆分文件 | 单文件计划 + github-app 片段 | 6 + 9 = 15 |
| 已拆分文件 | 原子化目录计划 | 12 |
| 拆分后文件总数 | 含 index + 原子单元 | 74 |
| 模块数 | 一级模块 | 6 |
| 校验通过 | — | 27 / 27 (100%) |
| 内容丢失 | — | 0 |

## 按模块分布

| 模块 | 原始文件数 | 拆分后文件数 | 迁移状态 |
|------|-----------|------------|---------|
| `ai-docs/` | 3 | 8 | ✅ 完成 |
| `agent-system/` | 5 | 21 | ✅ 完成 |
| `exploration/` | 4 | 16 | ✅ 完成 |
| `github-integration/` | 2 + 9 片段 | 14 | ✅ 完成 |
| `docs-governance/` | 3 | 8 | ✅ 完成 |
| `python-environment/` | 1 | 7 | ✅ 完成 |
| **合计** | **27** | **74** | **✅ 全部完成** |

## 校验说明

- **校验状态**：✅ 通过表示文件已成功迁移至目标路径，且内容完整、引用关系已更新
- **拆分说明**：标记"是"的原始文件已原子化拆分为多个独立单元，每个单元可独立阅读
- **github-app 片段**：#19-#27 为 `2026-05-22-github-app-installation-token-override.md` 拆分后的 9 个片段（不含 index.md），单独列出以覆盖全部原始内容
- **别名声明**：已拆分的计划在新目录的 `index.md` 头部添加了别名声明（如"曾用名 2026-05-22-github-app-installation-token-override.md，已原子化拆分"）
