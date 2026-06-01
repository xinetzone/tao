# 更新日志

本文件为项目变更日志的导航索引。变更记录按层级拆分至以下位置：

- **各功能模块**的详细变更记录 → `.agents/skills/<模块>/CHANGELOG.md`
- **项目级别**（跨模块）变更记录 → `tests/project_changelogs/CHANGELOG_<年月>.md`（按时间拆分）

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.2.0] - 2026-06-01 — Harness 智能体系统

引入 Harness 全栈 Agent 治具，实现 LangGraph 与 Metaflow 对等深度集成的 6 层架构骨架与三大跨层交互模式。

### Added

- **6 层架构模块**：落地 Harness 智能体系统六层结构骨架。
  - `core/`：状态管理、桥接适配、注册表（`StateView`、`UnifiedStateManager`、`BridgeConfig`、`NodeToStepAdapter`、`StepToGraphAdapter`、`AgentRegistry`、`FlowRegistry`）。
  - `runtime/`：执行器、调度器、检查点（`GraphExecutor`、`FlowExecutor`、`UnifiedExecutor`、`HybridScheduler`、`HarnessCheckpointer` 及 `MemoryBackend`/`RedisBackend`）。
  - `agents/`：LangGraph Agent 抽象与模板（`GraphAgent`、`ReActAgent`、`PlanAndExecuteAgent`、`RouterAgent`）。
  - `pipelines/`：Metaflow 流水线基类与模板（`HarnessFlow`、`EvalFlow`、`ETLFlow`、`TrainingFlow`）。
  - `eval/`：评估治具、指标协议与多格式 Reporter（`EvalHarness`、`EvalSuite`、`Metric` Protocol、`ExactMatch`、`LatencyMetric`、`ConsoleReporter`、`JsonReporter`、`MarkdownReporter`）。
  - `devtools/`：状态检视、回放与性能剖析（`StateInspector`、`ReplayEngine`、`ExecutionRecording`、`PerformanceProfiler`、`@profiled`）。
- **三大跨层交互模式**：
  - **Agent-as-Step**：将 LangGraph Agent 包装为 Metaflow Step 可调用函数。
  - **Flow-as-Tool**：将 Metaflow Flow 注册为 Agent 可调用 Tool。
  - **Shared Checkpoint**：跨层持久化适配器统一 LangGraph Checkpointer 与 Metaflow Artifact Store 的状态视图。
- **Phase 0 兼容性验证脚本** [`scripts/verify_harness_compat.py`](scripts/verify_harness_compat.py)：覆盖 Python、LangGraph、Metaflow 与可选依赖的导入与最小冒烟用例。
- **`harness` 依赖组**：在 `pyproject.toml` 中新增 `optional-dependencies.harness`，包含 `langgraph`、`metaflow`、`pydantic`、`redis`；同步开发组 `harness-dev` 含 `langgraph-cli`、`pytest-asyncio` 等。
- **架构归档文档** [`.agents/docs/harness-architecture.md`](.agents/docs/harness-architecture.md)：沉淀 Harness 系统的分层架构、关键设计决策、依赖约束、平台限制与模块清单，作为后续 AI 与人类协作者的参考入口。

### Verified

- **Python 3.14 + LangGraph 1.2.2 兼容性**：在 Python 3.14.5 运行时下完成导入、状态机构建与 Checkpointer 路径冒烟，结论为通过。
- **Metaflow 2.19.31 Linux 兼容**：在 Linux 容器内完成最小 Flow 的本地执行验证，结论为通过。

### Known Limitations

- **Metaflow 在 Windows 上不可用**：依赖 POSIX 专属 `fcntl` 模块，Windows 解释器导入即失败。Harness 已通过 `TYPE_CHECKING` 守卫与延迟导入将其隔离至 `pipelines/` 与 `runtime/` 的 Metaflow 路径，Windows 下 LangGraph 路径完全可用；如需运行 Metaflow 路径，请使用 WSL 或 Linux 容器。

## 模块变更日志索引

| 模块 | 说明 | CHANGELOG 路径 |
|------|------|---------------|
| Skill Creator | 技能开发工具链 | [.agents/skills/skill-creator/CHANGELOG.md](.agents/skills/skill-creator/CHANGELOG.md) |
| Task Execution Summary | 任务执行总结报告生成器 | [.agents/skills/task-execution-summary/CHANGELOG.md](.agents/skills/task-execution-summary/CHANGELOG.md) |

## 项目级变更日志索引

项目级别（跨模块）的变更记录按时间拆分，存放在 `tests/project_changelogs/` 目录下：

| 时间 | 说明 | CHANGELOG 路径 |
|------|------|---------------|
| 2026-05 | 2026年5月项目级变更（[未发布]） | [tests/project_changelogs/CHANGELOG_2026-05.md](tests/project_changelogs/CHANGELOG_2026-05.md) |

> 说明：上述路径为变更记录的**真实数据源**。文档站点（Sphinx）通过 [`docs/tech/changelog.md`](../../docs/tech/changelog.md) 与 [`docs/tech/changelogs/`](../../docs/tech/changelogs/) 下的镜像页 `{include}` 引用渲染，请勿直接编辑镜像页。
